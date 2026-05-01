from __future__ import annotations

import asyncio
import re
import shlex
from dataclasses import dataclass
from pathlib import Path


ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
DELETE_REQUEST_RE = re.compile(
    r"\b(удали|удалить|удаление|сотри|стереть|снеси|очисти|очистить|"
    r"delete|remove|unlink|rmdir|trash)\b|\brm\s+-|shutil\.rmtree|send2trash",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class OpenCodeResult:
    ok: bool
    output: str
    error: str
    return_code: int | None
    command: str


class OpenCodeBridge:
    def __init__(
        self,
        *,
        command: str,
        workspace: Path,
        timeout_seconds: int,
        max_output_chars: int,
        enabled: bool,
        agent: str | None = None,
        agent_file: Path | None = None,
    ) -> None:
        self.command = command
        self.workspace = workspace
        self.timeout_seconds = timeout_seconds
        self.max_output_chars = max_output_chars
        self.enabled = enabled
        self.agent = agent
        self.agent_file = agent_file

    async def ask(self, prompt: str) -> OpenCodeResult:
        if self._contains_delete_request(prompt):
            return OpenCodeResult(
                ok=False,
                output="",
                error="Deletion requests are blocked by Thursday Core before OpenCode execution.",
                return_code=None,
                command=self.command,
            )

        if not self.enabled:
            return OpenCodeResult(
                ok=False,
                output="",
                error="OpenCode bridge disabled by OPENCODE_ENABLED=false",
                return_code=None,
                command=self.command,
            )

        if not self.workspace.exists():
            return OpenCodeResult(
                ok=False,
                output="",
                error=f"Workspace does not exist: {self.workspace}",
                return_code=None,
                command=self.command,
            )

        try:
            command_parts = self._build_command_parts(self._build_prompt(prompt))
            if not command_parts:
                return OpenCodeResult(
                    ok=False,
                    output="",
                    error="OPENCODE_COMMAND is empty",
                    return_code=None,
                    command=self.command,
                )

            process = await asyncio.create_subprocess_exec(
                *command_parts,
                cwd=self.workspace,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=self.timeout_seconds
            )
        except FileNotFoundError:
            return OpenCodeResult(
                ok=False,
                output="",
                error=f"CLI command not found: {self.command}",
                return_code=None,
                command=self.command,
            )
        except TimeoutError:
            process.kill()
            await process.wait()
            return OpenCodeResult(
                ok=False,
                output="",
                error=f"OpenCode timed out after {self.timeout_seconds} seconds",
                return_code=None,
                command=self.command,
            )

        output = self._trim(self._clean_output(stdout.decode("utf-8", errors="replace")))
        error = self._trim(self._clean_output(stderr.decode("utf-8", errors="replace")))
        return OpenCodeResult(
            ok=process.returncode == 0,
            output=output,
            error=error,
            return_code=process.returncode,
            command=" ".join(command_parts[:-1]),
        )

    def _build_command_parts(self, prompt: str) -> list[str]:
        command_parts = shlex.split(self.command)
        if not command_parts:
            return []

        executable = Path(command_parts[0]).name
        if executable == "opencode" and len(command_parts) == 1:
            command_parts.append("run")

        if executable == "opencode" and "run" in command_parts and self.agent:
            has_agent_flag = "--agent" in command_parts or any(
                part.startswith("--agent=") for part in command_parts
            )
            if not has_agent_flag:
                command_parts.extend(["--agent", self.agent])

        return [*command_parts, prompt]

    def _build_prompt(self, prompt: str) -> str:
        if not self.agent_file or not self.agent_file.exists():
            return prompt
        return (
            "Hard safety rule: do not delete files or folders. Do not run rm, rmdir, unlink, "
            "shutil.rmtree, trash operations, git reset --hard, or destructive cleanup commands. "
            "If the user asks for deletion, refuse.\n\n"
            "Use the local assistant instructions from AGENT.md before answering.\n"
            f"AGENT.md path: {self.agent_file}\n\n"
            f"User Telegram request:\n{prompt}"
        )

    def _contains_delete_request(self, prompt: str) -> bool:
        return bool(DELETE_REQUEST_RE.search(prompt))

    def _clean_output(self, value: str) -> str:
        without_ansi = ANSI_ESCAPE_RE.sub("", value)
        lines = [line.rstrip() for line in without_ansi.splitlines()]
        return "\n".join(line for line in lines if line.strip()).strip()

    def _trim(self, value: str) -> str:
        if len(value) <= self.max_output_chars:
            return value
        return value[: self.max_output_chars] + "\n...[output trimmed]"
