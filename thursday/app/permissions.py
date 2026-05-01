from __future__ import annotations


class PermissionLayer:
    def __init__(self, allowed_user_ids: set[int]) -> None:
        self.allowed_user_ids = allowed_user_ids

    def is_allowed_telegram_user(self, user_id: int | None) -> bool:
        return user_id is not None and user_id in self.allowed_user_ids
