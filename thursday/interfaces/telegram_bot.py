from __future__ import annotations

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from thursday.app.action_log import ActionEvent, ActionLog
from thursday.app.permissions import PermissionLayer
from thursday.app.router import CommandRouter
from thursday.app.session_store import SessionStore, TelegramSessionMessage


class TelegramInterface:
    def __init__(
        self,
        *,
        token: str,
        permissions: PermissionLayer,
        router: CommandRouter,
        action_log: ActionLog,
        session_store: SessionStore,
    ) -> None:
        self.token = token
        self.permissions = permissions
        self.router = router
        self.action_log = action_log
        self.session_store = session_store

    def run(self) -> None:
        app = Application.builder().token(self.token).build()
        app.add_handler(CommandHandler("start", self._start))
        app.add_handler(CommandHandler("status", self._handle_message))
        app.add_handler(CommandHandler("help", self._handle_message))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))
        app.run_polling(allowed_updates=Update.ALL_TYPES)

    async def _start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        del context
        user_id = update.effective_user.id if update.effective_user else None
        if not self.permissions.is_allowed_telegram_user(user_id):
            await self._deny(update, user_id)
            return

        await update.effective_message.reply_text(
            "Thursday online. Напиши задачу, и я передам её в OpenCode."
        )

    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        del context
        user_id = update.effective_user.id if update.effective_user else None
        message = update.effective_message
        if message is None:
            return

        if not self.permissions.is_allowed_telegram_user(user_id):
            await self._deny(update, user_id)
            return

        text = message.text or ""
        await message.chat.send_action(ChatAction.TYPING)
        result = await self.router.handle_text(text)
        session_path = self.session_store.append_telegram_exchange(
            TelegramSessionMessage(
                chat_id=message.chat_id,
                user_id=user_id,
                username=update.effective_user.username if update.effective_user else None,
                user_text=text,
                assistant_text=result.text,
                ok=result.ok,
            )
        )

        self.action_log.write(
            ActionEvent(
                action="telegram_message",
                user_id=user_id,
                status="ok" if result.ok else "error",
                details={
                    "input": text,
                    "response_preview": result.text[:500],
                    "session_path": session_path.as_posix(),
                },
            )
        )
        await self._reply_chunks(update, result.text)

    async def _deny(self, update: Update, user_id: int | None) -> None:
        self.action_log.write(
            ActionEvent(
                action="telegram_denied",
                user_id=user_id,
                status="denied",
                details={},
            )
        )
        if update.effective_message:
            await update.effective_message.reply_text("Access denied.")

    async def _reply_chunks(self, update: Update, text: str) -> None:
        if not update.effective_message:
            return
        chunks = [text[index : index + 3900] for index in range(0, len(text), 3900)] or [""]
        for chunk in chunks:
            await update.effective_message.reply_text(chunk)
