from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ActionEvent:
    action: str
    user_id: int | None
    status: str
    details: dict[str, Any]
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class ActionLog:
    def __init__(self, path: Path) -> None:
        self.path = path

    def write(self, event: ActionEvent) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")
