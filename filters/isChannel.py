from aiogram import types
from aiogram.filters import BaseFilter

import config

class IsChannel(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        return message.chat.id == config.channel