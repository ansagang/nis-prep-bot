import asyncio
import os

from dotenv import find_dotenv, load_dotenv
from aiogram import Bot, Dispatcher
load_dotenv(find_dotenv())
import config

from middleware import CheckAdmin
from handlers import setup_message_routers
from callbacks import setup_callback_routers
from aiogram.enums import ParseMode
from database import sqlite

async def main():
    bot = Bot(token=os.getenv('TOKEN'), parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    dp.message.middleware(CheckAdmin())
    dp.callback_query.middleware(CheckAdmin())

    message_routers = setup_message_routers()
    callback_routers = setup_callback_routers()
    dp.include_router(message_routers)
    dp.include_router(callback_routers)
    getChat = await bot.get_chat(chat_id=config.channel)
    config.linked_chat_id = getChat.linked_chat_id

    await dp.start_polling(bot, skip_updates=True, on_startup=sqlite.sql_start())
    await bot.delete_webhook(drop_pending_updates=True)

if __name__ == "__main__":
    asyncio.run(main())