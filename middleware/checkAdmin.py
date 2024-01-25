from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
import config
from aiogram import types

class CheckAdmin(BaseMiddleware):
    async def __call__(self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]], event: CallbackQuery | Message, data: Dict[str, Any]) -> Any:
        def checkAdmin():
            if event.from_user.id in config.admin:
                return True
            else:
                return False
        data['isAdmin'] = checkAdmin()
        status = await event.bot.get_chat_member(chat_id=config.channel, user_id=event.from_user.id)
        if status.status not in ["member", "creator", "administrator", "owner"]:
            return await event.answer("Для использования бота необходимо быть подписанным на канал\n-https://t.me/+H84YQ_dEzzxmMzgy\n")

        return await handler(event, data)