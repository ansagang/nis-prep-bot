from random import choice

from aiogram import types, Router, F
from aiogram.filters import Command, or_f

from database import sqlite

from keyboards import main_kb, inline_builder

from utils import get_project_root

from filters import IsChannel

router = Router()

@router.message(or_f(Command('start'), F.text == "Меню"))
async def menu_cmd(message: types.Message, isAdmin: bool):
    filename = get_project_root('assets/logo.png')
    kb = main_kb.inlineKb(isAdmin)
    await message.bot.send_photo(chat_id=message.from_user.id, photo=types.FSInputFile(path=filename), caption='', reply_markup=kb)
    await message.delete()

@router.message(or_f(Command('help'), F.text == "Возможности"))
async def help_cmd(message: types.Message):
    filename = get_project_root('assets/logo.png')
    caption = (
        "Возможности:\n"
        "\n"
        "<b>Как вызвать меню ❓</b>\n"
        "-Используйте команду /menu либо же напишите Меню\n"
        "\n"
        "<b>Информация о боте ❓</b>\n"
        "-Используйте команду /info либо же напишите Информация\n"
        "\n"
        "<b>Как получить случайный материал ❓</b>\n"
        "-Используйте команду /random_material\n"
        "\n"
        "<b>Как получить случайный пробник ❓</b>\n"
        "-Используйте команду /random_test\n"
    )
    await message.bot.send_photo(chat_id=message.from_user.id, photo=types.FSInputFile(path=filename), caption=caption, reply_markup=inline_builder(text='« Назад', callback_data='delete'))
    await message.delete()

@router.message(or_f(Command('info'), F.text == "Информация"))
async def info_cmd(message: types.Message):
    filename = get_project_root('assets/logo.png')
    caption = (
        "🌱 Я мультифункциональный, удобный и эргономичный бот для подготовки к поступлению в Назарбаевские Интеллектуальные Школы.\n"
        "\n"
        "<b>Мой создатель:</b>\n"
        "-@ansagang \n"
        "\n"
        "<b>Телеграм канал:</b>\n"
        "-https://t.me/+H84YQ_dEzzxmMzgy\n"
    )
    await message.bot.send_photo(chat_id=message.from_user.id, photo=types.FSInputFile(path=filename), caption=caption, reply_markup=inline_builder(text='« Назад', callback_data='delete'))
    await message.delete()

@router.message(Command('random_test'))
async def random_test(message: types.Message):
    test = await sqlite.sql_random_test()
    pattern = {}
    pattern['reply_markup'] = inline_builder(text='« Назад', callback_data='delete', sizes=1)
    pattern['chat_id'] = message.from_user.id
    if test:
        pattern['caption'] = (
            "<b>"+test[1]+"</b>\n"
            "\n"
            "📄 "+test[2]
        )
        pattern['document']: test[0]
        await message.bot.send_document(**pattern)
    else:
        pattern['text'] = (
            "<b>Нету тестов</b>"
        )
        await message.bot.send_message(**pattern)
    await message.delete()

@router.message(Command('random_material'))
async def random_material(message: types.Message):
    material = await sqlite.sql_random_material()
    pattern = {}
    pattern['reply_markup'] = inline_builder(text='« Назад', callback_data='delete', sizes=1)
    pattern['chat_id'] = message.from_user.id
    if material:
        pattern['caption'] = (
            "<b>"+material[1]+"</b>\n"
            "\n"
            "📚 "+material[2]
        ),
        pattern['photo']: material[0]
        await message.bot.send_photo(**pattern)
    else:
        pattern['text'] = (
            "<b>Нету материала</b>"
        )
        await message.bot.send_message(**pattern)
    await message.delete()

# @router.message(and_f(IsGroup(), isCussword()))
# async def words_filter(message: types.Message):
#     await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    
@router.channel_post(IsChannel())
async def react(message: types.Message):
    emojis = ["👍", "❤️", "🔥", "👏", "💯"]
    react = types.ReactionTypeEmoji(emoji=choice(emojis))
    await message.react([react])