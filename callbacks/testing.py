from aiogram import Router, F
from aiogram import types

from database import sqlite

from keyboards import inline_builder
from keyboards import main_kb

from utils import KeyboardPaginator, get_project_root

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from aiogram.filters import or_f
from json import loads, dumps
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

def compose_markup(question: int, testing_id):
    cd1 = {
        "q": question,
        "a": 0,
        "id": testing_id
    }
    cd2 = {
        "q": question,
        "a": 1,
        "id": testing_id
    }
    cd3 = {
        "q": question,
        "a": 2,
        "id": testing_id
    }
    cd4 = {
        "q": question,
        "a": 3,
        "id": testing_id
    }
    km = inline_builder(text=['A', 'B', 'C', 'D', 'Остановить тестирование'], callback_data=[dumps(cd1), dumps(cd2), dumps(cd3), dumps(cd4), 'stop_'+testing_id], sizes=[4, 1])
    
    return km


def reset(uid: int, testing_id):
    sqlite.set_in_process(uid, False, testing_id)
    sqlite.change_questions_passed(uid, 0, testing_id)
    sqlite.change_questions_message(uid, 0, testing_id)
    sqlite.change_current_question(uid, 0, testing_id)

@router.callback_query(F.data.startswith('testing_'))
async def go_handler(query: types.CallbackQuery):
    testing_id = query.data.split(sep="_", maxsplit=1)[1]
    reset(query.from_user.id, testing_id)
    testing = await sqlite.sql_get_testing(testing_id)
    if not sqlite.is_exists(query.from_user.id, testing_id):
        sqlite.add(query.from_user.id, testing_id)
    if sqlite.is_in_process(query.from_user.id, testing_id):
        await query.bot.send_message(query.from_user.id, "🚫 Вы не можете начать тест, потому что вы уже его проходите\\.", parse_mode="MarkdownV2")
        return
    sqlite.set_in_process(query.from_user.id, True, testing_id)
    msg = await query.bot.send_photo(
        chat_id=query.from_user.id,
        photo=testing[0][0],
        caption=f"[{testing[0][3]}] {testing[0][2]}",
        reply_markup=compose_markup(0, testing_id),
        parse_mode="MarkdownV2"
    )
    sqlite.change_questions_message(query.from_user.id, msg.message_id, testing_id)
    sqlite.change_current_question(query.from_user.id, 0, testing_id)
    sqlite.change_questions_passed(query.from_user.id, 0, testing_id)

async def quit(query):
    testing_id = query.data.split(sep="_", maxsplit=1)[1]
    passed = sqlite.get_questions_passed(query.from_user.id, testing_id)
    testing = await sqlite.sql_get_testing(testing_id)
    if not sqlite.is_in_process(query.from_user.id, testing_id):
        
        # await query.bot.send_message(query.from_user.id, "❗️Вы еще не начали тест\\.", parse_mode="MarkdownV2")
        return
    
    sqlite.change_user(query.from_user.id, testing_id, f"{passed}/{len(testing)}", query.from_user.username)
    reset(query.from_user.id, testing_id)

@router.callback_query(F.data.startswith('stop_'))
async def quit_handler(query: types.CallbackQuery):
    testing_id = query.data.split(sep="_", maxsplit=1)[1]
    passed = sqlite.get_questions_passed(query.from_user.id, testing_id)
    testing = await sqlite.sql_get_testing(testing_id)
    photo = get_project_root('assets/logo.png')
    pattern = {
        "caption": (
            "<b>Вы успешно завершили тест!</b>"
            "\n"
            f"Ваш результат: <b>{passed} из {len(testing)}</b>"
        ),
        "reply_markup": inline_builder(text='« Назад', callback_data='delete', sizes=1),
        "chat_id": query.from_user.id,
        "photo": types.FSInputFile(path=photo)
    }
    await query.bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    await query.bot.send_photo(**pattern)
    await quit(query)

@router.callback_query(lambda c: True)
async def tests(query: types.CallbackQuery):
    data = loads(query.data)
    q = data['q']
    testing_id = data['id']
    testing = await sqlite.sql_get_testing(testing_id)
    is_correct = int(testing[q][1]) == data['a']
    passed = sqlite.get_questions_passed(query.from_user.id, testing_id)
    msg = sqlite.get_questions_message(query.from_user.id, testing_id)
    if is_correct:
        passed += 1
        sqlite.change_questions_passed(query.from_user.id, passed, testing_id)
    if q + 1 > len(testing) - 1:
        sqlite.change_user(query.from_user.id, testing_id, f"{passed}/{len(testing)}", query.from_user.username)
        reset(query.from_user.id, testing_id)
        await query.bot.delete_message(query.from_user.id, msg)
        photo = get_project_root('assets/logo.png')
        pattern = {
            "caption": (
                "<b>Ура!</b>\n"
                "\n"
                "Вы успешно завершили тест!"
                "\n"
                f"Ваш результат: <b>{passed} из {len(testing)}</b>"
            ),
            "reply_markup": inline_builder(text='« Назад', callback_data='delete', sizes=1),
            "chat_id": query.from_user.id,
            "photo": types.FSInputFile(path=photo)
        }
        await query.bot.send_photo(**pattern)
        return
    
    await query.bot.edit_message_media(
        media=types.InputMediaPhoto(media=testing[q + 1][0]),
        chat_id=query.from_user.id,
        message_id=msg,
        reply_markup=compose_markup(q + 1, testing_id),
    )
    await query.bot.edit_message_caption(
        caption=f"[{testing[q + 1][3]}] {testing[q + 1][2]}",
        chat_id=query.from_user.id,
        message_id=msg,
        reply_markup=compose_markup(q + 1, testing_id),
        parse_mode="MarkdownV2"
    )