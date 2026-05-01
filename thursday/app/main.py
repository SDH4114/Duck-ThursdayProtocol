from __future__ import annotations

from thursday.app.action_log import ActionLog
from thursday.app.agent_profile import ensure_agent_file
from thursday.app.config import Settings
from thursday.app.permissions import PermissionLayer
from thursday.app.router import CommandRouter
from thursday.app.session_store import SessionStore
from thursday.interfaces.telegram_bot import TelegramInterface
from thursday.tools.files import SafeFileReader
from thursday.tools.opencode import OpenCodeBridge
from thursday.tools.web import WebReader


def build_telegram_interface(settings: Settings) -> TelegramInterface:
    ensure_agent_file(settings.agent_file_path)
    action_log = ActionLog(settings.action_log_path)
    session_store = SessionStore(settings.session_dir)
    file_reader = SafeFileReader(settings.allowed_read_dirs)
    web_reader = WebReader()
    permissions = PermissionLayer(settings.telegram_allowed_user_ids)
    opencode = OpenCodeBridge(
        command=settings.opencode_command,
        workspace=settings.opencode_workspace,
        timeout_seconds=settings.opencode_timeout_seconds,
        max_output_chars=settings.opencode_max_output_chars,
        enabled=settings.opencode_enabled,
        agent=settings.opencode_agent,
        agent_file=settings.agent_file_path,
    )
    router = CommandRouter(opencode, session_store, file_reader, web_reader)
    return TelegramInterface(
        token=settings.telegram_bot_token,
        permissions=permissions,
        router=router,
        action_log=action_log,
        session_store=session_store,
    )


def main() -> None:
    settings = Settings.from_env()
    settings.validate()
    build_telegram_interface(settings).run()


if __name__ == "__main__":
    main()
