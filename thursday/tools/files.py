from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


TEXT_SUFFIXES = {
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".css",
    ".html",
}


@dataclass(frozen=True)
class FileReadResult:
    ok: bool
    text: str


class SafeFileReader:
    def __init__(self, allowed_dirs: list[Path], *, max_chars: int = 6000) -> None:
        self.allowed_dirs = [path.expanduser().resolve() for path in allowed_dirs]
        self.max_chars = max_chars

    def read_path(self, raw_path: str) -> FileReadResult:
        path = Path(raw_path).expanduser().resolve()
        if not self._is_allowed(path):
            return FileReadResult(
                ok=False,
                text=(
                    "Чтение запрещено: путь вне разрешённых директорий.\n"
                    f"Путь: {path}\n\n"
                    "Разрешённые директории:\n"
                    + "\n".join(f"- {allowed}" for allowed in self.allowed_dirs)
                ),
            )

        if not path.exists():
            return FileReadResult(ok=False, text=f"Файл или папка не найдены: {path}")

        if path.is_dir():
            return self._read_directory(path)

        return self._read_file(path)

    def _read_file(self, path: Path) -> FileReadResult:
        if path.suffix.lower() not in TEXT_SUFFIXES:
            return FileReadResult(ok=False, text=f"Не читаю бинарный или неизвестный тип файла: {path}")

        content = path.read_text(encoding="utf-8", errors="replace")
        return FileReadResult(ok=True, text=f"# {path}\n\n{self._trim(content)}")

    def _read_directory(self, path: Path) -> FileReadResult:
        files = sorted(
            item for item in path.iterdir() if item.is_file() and item.suffix.lower() in TEXT_SUFFIXES
        )
        if not files:
            return FileReadResult(ok=True, text=f"В папке нет читаемых текстовых файлов: {path}")

        parts = [f"# Directory: {path}", ""]
        for file_path in files[:8]:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            parts.append(f"## {file_path.name}\n")
            parts.append(self._trim(content, max_chars=1200))
            parts.append("")

        if len(files) > 8:
            parts.append(f"...ещё {len(files) - 8} файлов не показаны")

        return FileReadResult(ok=True, text=self._trim("\n".join(parts)))

    def _is_allowed(self, path: Path) -> bool:
        return any(path == allowed or allowed in path.parents for allowed in self.allowed_dirs)

    def _trim(self, value: str, *, max_chars: int | None = None) -> str:
        limit = max_chars or self.max_chars
        if len(value) <= limit:
            return value
        return value[:limit] + "\n...[trimmed]"
