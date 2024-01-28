from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

import config

class CheckAdmin(BaseMiddleware):
    async def __call__(self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]], event: CallbackQuery | Message, data: Dict[str, Any]) -> Any:
        
        status = await event.bot.get_chat_member(chat_id=config.channel, user_id=event.from_user.id)
        if status.status not in ["member", "creator", "administrator", "owner"] and event.chat.type == 'private':
            return await event.answer("Для использования бота необходимо быть подписанным на канал\n-https://t.me/+H84YQ_dEzzxmMzgy\n")
        elif status.status in ["creator", "administrator", "owner"]:
            config.admin.append(event.from_user.id)
        def checkAdmin():
            if event.from_user.id in config.admin:
                return True
            else:
                return False
        data['isAdmin'] = checkAdmin()

        return await handler(event, data)