from __future__ import annotations

import os
import json
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # Allows importing core modules before dependencies are installed.
    def load_dotenv() -> bool:
        return False


def _parse_user_ids(raw_value: str) -> set[int]:
    ids: set[int] = set()
    for value in raw_value.split(","):
        value = value.strip()
        if not value:
            continue
        try:
            ids.add(int(value))
        except ValueError as exc:
            raise ValueError(f"Invalid Telegram user id: {value!r}") from exc
    return ids


def _parse_bool(raw_value: str, *, default: bool) -> bool:
    if not raw_value:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_paths(raw_value: str) -> list[Path]:
    paths: list[Path] = []
    for value in raw_value.split(":"):
        value = value.strip()
        if value:
            paths.append(Path(value).expanduser().resolve())
    return paths


@dataclass(frozen=True)
class Settings:
    thursday_home: Path
    telegram_bot_token: str
    telegram_allowed_user_ids: set[int]
    opencode_command: str
    opencode_workspace: Path
    opencode_agent: str | None
    opencode_timeout_seconds: int
    opencode_max_output_chars: int
    opencode_enabled: bool
    action_log_path: Path
    session_dir: Path
    agent_file_path: Path
    allowed_read_dirs: list[Path]

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()

        thursday_home = Path(
            os.getenv("THURSDAY_HOME", "~/aiwork/thusday")
        ).expanduser().resolve()
        workspace = Path(
            os.getenv("OPENCODE_WORKSPACE", thursday_home.as_posix())
        ).expanduser().resolve()
        opencode_config_path = thursday_home / "opencode.json"
        opencode_agent = os.getenv("OPENCODE_AGENT", "").strip() or _read_default_agent(
            opencode_config_path
        )
        default_allowed_read_dirs = ":".join(
            [
                thursday_home.as_posix(),
                "~/aiwork/data-obsidian/projects/Thursday",
                Path.cwd().as_posix(),
            ]
        )

        return cls(
            thursday_home=thursday_home,
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", "").strip(),
            telegram_allowed_user_ids=_parse_user_ids(
                os.getenv("TELEGRAM_ALLOWED_USER_IDS", "")
            ),
            opencode_command=os.getenv("OPENCODE_COMMAND", "opencode").strip(),
            opencode_workspace=workspace,
            opencode_agent=opencode_agent,
            opencode_timeout_seconds=int(os.getenv("OPENCODE_TIMEOUT_SECONDS", "300")),
            opencode_max_output_chars=int(os.getenv("OPENCODE_MAX_OUTPUT_CHARS", "3500")),
            opencode_enabled=_parse_bool(os.getenv("OPENCODE_ENABLED", "true"), default=True),
            action_log_path=thursday_home / "logs" / "actions.jsonl",
            session_dir=thursday_home / "sessions",
            agent_file_path=thursday_home / "AGENT.md",
            allowed_read_dirs=_parse_paths(
                os.getenv("THURSDAY_ALLOWED_READ_DIRS", default_allowed_read_dirs)
            ),
        )

    def validate(self) -> None:
        self.ensure_runtime_dirs()
        if not self.telegram_bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        if not self.telegram_allowed_user_ids:
            raise ValueError("TELEGRAM_ALLOWED_USER_IDS is required")
        if not self.opencode_command:
            raise ValueError("OPENCODE_COMMAND is required")
        if not self.opencode_workspace.exists():
            raise ValueError(f"OPENCODE_WORKSPACE does not exist: {self.opencode_workspace}")

    def ensure_runtime_dirs(self) -> None:
        self.thursday_home.mkdir(parents=True, exist_ok=True)
        self.opencode_workspace.mkdir(parents=True, exist_ok=True)
        self.action_log_path.parent.mkdir(parents=True, exist_ok=True)
        self.session_dir.mkdir(parents=True, exist_ok=True)


def _read_default_agent(config_path: Path) -> str | None:
    if not config_path.exists():
        return None
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    default_agent = data.get("default_agent")
    if isinstance(default_agent, str) and default_agent.strip():
        return default_agent.strip()
    return None
