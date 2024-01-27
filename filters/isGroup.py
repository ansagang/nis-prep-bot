from aiogram.filters import BaseFilter
from aiogram import types
import config

class IsGroup(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        return message.chat.id == config.linked_chat_id