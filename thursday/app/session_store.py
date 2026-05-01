from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path


@dataclass(frozen=True)
class TelegramSessionMessage:
    chat_id: int
    user_id: int | None
    username: str | None
    user_text: str
    assistant_text: str
    ok: bool


class SessionStore:
    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir

    def append_telegram_exchange(self, message: TelegramSessionMessage) -> Path:
        self.session_dir.mkdir(parents=True, exist_ok=True)
        now = datetime.now(UTC)
        path = self.session_dir / f"telegram-{message.chat_id}-{now:%Y-%m-%d}.md"

        if not path.exists():
            path.write_text(
                "# Telegram Dialogue Session\n\n"
                f"- chat_id: `{message.chat_id}`\n"
                f"- created_at: `{now.isoformat()}`\n\n",
                encoding="utf-8",
            )

        with path.open("a", encoding="utf-8") as file:
            file.write(f"## {now.isoformat()}\n\n")
            file.write(f"- user_id: `{message.user_id}`\n")
            if message.username:
                file.write(f"- username: `@{message.username}`\n")
            file.write(f"- status: `{'ok' if message.ok else 'error'}`\n\n")
            file.write("### User\n\n")
            file.write(self._fenced(message.user_text))
            file.write("\n\n### Thursday / OpenCode\n\n")
            file.write(self._fenced(message.assistant_text))
            file.write("\n\n")

        return path

    def read_by_date(self, target_date: date, *, max_chars: int = 6000) -> str | None:
        self.session_dir.mkdir(parents=True, exist_ok=True)
        pattern = f"telegram-*-{target_date:%Y-%m-%d}.md"
        files = sorted(self.session_dir.glob(pattern))
        if not files:
            return None

        parts: list[str] = []
        for path in files:
            parts.append(f"# {path.name}\n")
            parts.append(path.read_text(encoding="utf-8", errors="replace"))

        content = "\n\n".join(parts)
        if len(content) <= max_chars:
            return content
        return content[:max_chars] + "\n...[trimmed]"

    def _fenced(self, value: str) -> str:
        fence = "```"
        while fence in value:
            fence += "`"
        return f"{fence}text\n{value}\n{fence}"
