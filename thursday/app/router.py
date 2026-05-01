from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

from thursday.app.session_store import SessionStore
from thursday.tools.files import SafeFileReader
from thursday.tools.opencode import OpenCodeBridge, OpenCodeResult
from thursday.tools.web import WebReader


DATE_DMY_RE = re.compile(r"\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b")
DATE_ISO_RE = re.compile(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b")
PATH_RE = re.compile(r"(?:~|/)[^\n\r]+")
DELETE_REQUEST_RE = re.compile(
    r"\b(удали|удалить|удаление|сотри|стереть|снеси|очисти|очистить|"
    r"delete|remove|unlink|rmdir|trash)\b|\brm\s+-|shutil\.rmtree|send2trash",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class RouterResult:
    text: str
    ok: bool


class CommandRouter:
    def __init__(
        self,
        opencode: OpenCodeBridge,
        session_store: SessionStore,
        file_reader: SafeFileReader,
        web_reader: WebReader,
    ) -> None:
        self.opencode = opencode
        self.session_store = session_store
        self.file_reader = file_reader
        self.web_reader = web_reader

    async def handle_text(self, text: str) -> RouterResult:
        cleaned_text = text.strip()
        if not cleaned_text:
            return RouterResult(text="Напиши задачу для OpenCode.", ok=False)

        if cleaned_text in {"/help", "help", "помощь"}:
            return RouterResult(text=self._help_text(), ok=True)

        if cleaned_text == "/status":
            return RouterResult(text="Thursday online. Telegram → OpenCode bridge готов.", ok=True)

        if self._looks_like_delete_request(cleaned_text):
            return RouterResult(
                text=(
                    "Удаление файлов заблокировано настройками безопасности. "
                    "Я могу прочитать файл, объяснить его или помочь подготовить безопасный план, "
                    "но удалять ничего не буду."
                ),
                ok=False,
            )

        url = self.web_reader.extract_url(cleaned_text)
        if url and self._looks_like_web_read(cleaned_text):
            result = self.web_reader.read_url(url)
            return RouterResult(text=result.text, ok=result.ok)

        if self._looks_like_web_search(cleaned_text):
            query = self._extract_search_query(cleaned_text)
            result = self.web_reader.search(query)
            return RouterResult(text=result.text, ok=result.ok)

        session_date = self._extract_date(cleaned_text)
        if session_date and self._looks_like_dialogue_lookup(cleaned_text):
            content = self.session_store.read_by_date(session_date)
            if not content:
                return RouterResult(
                    text=f"Не нашёл сохранённых Telegram-диалогов за {session_date:%d.%m.%Y}.",
                    ok=False,
                )
            return RouterResult(
                text=f"Диалоги за {session_date:%d.%m.%Y}:\n\n{content}",
                ok=True,
            )

        path = self._extract_path(cleaned_text)
        if path and self._looks_like_file_read(cleaned_text):
            result = self.file_reader.read_path(path)
            return RouterResult(text=result.text, ok=result.ok)

        result = await self.opencode.ask(cleaned_text)
        return RouterResult(text=self._format_opencode_result(result), ok=result.ok)

    def _looks_like_delete_request(self, text: str) -> bool:
        return bool(DELETE_REQUEST_RE.search(text))

    def _looks_like_dialogue_lookup(self, text: str) -> bool:
        lowered = text.lower()
        return any(word in lowered for word in {"говорили", "диалог", "диалоги", "обсуждали", "переписка"})

    def _looks_like_file_read(self, text: str) -> bool:
        lowered = text.lower()
        return any(word in lowered for word in {"прочитай", "прочти", "покажи", "открой", "read"})

    def _looks_like_web_read(self, text: str) -> bool:
        lowered = text.lower()
        return any(word in lowered for word in {"прочитай", "прочти", "открой", "сайт", "страницу", "url", "read"})

    def _looks_like_web_search(self, text: str) -> bool:
        lowered = text.lower()
        return any(
            phrase in lowered
            for phrase in {
                "найди в интернете",
                "поищи в интернете",
                "загугли",
                "найди информацию",
                "поиск в интернете",
                "web search",
                "search web",
            }
        )

    def _extract_search_query(self, text: str) -> str:
        lowered = text.lower()
        prefixes = [
            "найди в интернете",
            "поищи в интернете",
            "загугли",
            "найди информацию",
            "поиск в интернете",
            "web search",
            "search web",
        ]
        for prefix in prefixes:
            index = lowered.find(prefix)
            if index >= 0:
                return text[index + len(prefix) :].strip(" :—-")
        return text.strip()

    def _extract_date(self, text: str) -> date | None:
        if match := DATE_DMY_RE.search(text):
            day, month, year = (int(value) for value in match.groups())
            return date(year, month, day)
        if match := DATE_ISO_RE.search(text):
            year, month, day = (int(value) for value in match.groups())
            return date(year, month, day)
        return None

    def _extract_path(self, text: str) -> str | None:
        match = PATH_RE.search(text)
        if not match:
            return None
        return match.group(0).strip().strip("'\"` .,")

    def _format_opencode_result(self, result: OpenCodeResult) -> str:
        if result.ok:
            if result.output:
                return result.output
            return (
                "OpenCode завершил задачу, но не вернул текст.\n"
                f"Команда: {result.command}\n"
                f"Код выхода: {result.return_code}\n\n"
                "Проверь, что в .env стоит OPENCODE_COMMAND=opencode run."
            )

        message = "OpenCode не смог выполнить задачу."
        message += f"\n\nКоманда: {result.command}"
        if result.return_code is not None:
            message += f"\nКод выхода: {result.return_code}"
        if result.output:
            message += f"\n\nstdout:\n{result.output}"
        if result.error:
            message += f"\n\nstderr:\n{result.error}"
        return message

    def _help_text(self) -> str:
        return (
            "Thursday Telegram bridge:\n"
            "- /status — проверить, что бот живой\n"
            "- /help — показать помощь\n"
            "- 'о чем мы говорили 30.04.2026' — прочитать сохранённый диалог за дату\n"
            "- 'прочитай файл /path/file.md' — безопасно прочитать файл\n"
            "- 'прочитай сайт https://example.com' — прочитать страницу\n"
            "- 'найди в интернете ...' — web search\n"
            "- любой другой текст будет отправлен в OpenCode/Codex\n\n"
            "Удаление файлов заблокировано."
        )
