from aiogram import types
from aiogram.filters import BaseFilter

class IsGroup(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        return message.chat.type in ['supergroup'] and message.from_user.id == 777000