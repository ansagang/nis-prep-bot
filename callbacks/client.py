from aiogram import Router, F
from aiogram import types

from database import sqlite

from keyboards import inline_builder
from keyboards import main_kb

from utils import KeyboardPaginator, get_project_root

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from aiogram.filters import or_f

router = Router()

class Testing(StatesGroup):
    score = State()
    number = State()
    testing_id = State()

@router.callback_query(F.data == "testing")
async def materials(query: types.CallbackQuery):
    ids = await sqlite.sql_get_testing_id()
    users = sqlite.get_user(query.from_user.id)
    results = []
    for user in users:
        results.append({'testing_id': user[5], 'result': user[6]})
    buttons = []
    for id in ids:
        buttons.append({'text':id[0], 'callback_data': 'testing_'+id[0]})
    additional_buttons = [
        [
            types.InlineKeyboardButton(text='« Назад', callback_data="menu"),
        ],
    ]
    paginator = KeyboardPaginator(
        data=buttons,
        router=router,
        per_page=5,
        per_row=1,
        additional_buttons=additional_buttons
    )
    stoke = ""
    for result in results:
        stoke += f"{result['testing_id']}: {result['result']} \n"
    pattern = {
        "caption": (
            "<b>Тестирование</b>\n"
            "\n"
            "Результаты 🏆:"
            "\n"
            f"{stoke}"
            "\n"
            "-Выберите тестирование"
        ),
        "reply_markup": paginator.as_markup()
    }
    await query.message.edit_caption(**pattern)
    await query.answer()

@router.callback_query(F.data == "materials")
async def materials(query: types.CallbackQuery):
    subjects = await sqlite.sql_get_materials_subjects()
    text = []
    callback = []
    for subject in subjects:
        text.append(subject[0])
        callback.append('materials_'+subject[0])
    text.append('« Назад')
    callback.append('menu')
    pattern = {
        "caption": (
            "<b>📚 Материалы</b>\n"
            "\n"
            "-Выберите предмет"
        ),
        "reply_markup": inline_builder(text=text, callback_data=callback, sizes=1)
    }
    await query.message.edit_caption(**pattern)
    await query.answer()

@router.callback_query(F.data.startswith('materials_'))
async def materials(query: types.CallbackQuery):
    materials = await sqlite.sql_get_materials(query.data.split(sep="_", maxsplit=1)[1])
    buttons = []
    for material in materials:
        buttons.append({'text':material[3], 'callback_data': 'material_'+material[3]})
    additional_buttons = [
        [
            types.InlineKeyboardButton(text='« Назад', callback_data="materials"),
        ],
    ]
    paginator = KeyboardPaginator(
        data=buttons,
        router=router,
        per_page=5,
        per_row=1,
        additional_buttons=additional_buttons
    )
    pattern = {
        "caption": (
            "<b>📚 Материалы</b>\n"
            "\n"
        ),
        "reply_markup": paginator.as_markup()
    }
    await query.message.edit_caption(**pattern)
    await query.answer()

@router.callback_query(F.data.startswith('material_'))
async def material(query: types.CallbackQuery):
    material = await sqlite.sql_get_material(query.data.replace('material_', ''))
    pattern = {
        "caption": (
            "<b>"+material[1]+"</b>\n"
            "\n"
            "📚 "+material[2]
        ),
        "reply_markup": inline_builder(text='« Назад', callback_data='delete', sizes=1),
        "photo": material[0]
    }
    await query.message.answer_photo(**pattern)
    await query.answer()

@router.callback_query(F.data == "tests")
async def tests(query: types.CallbackQuery):
    subjects = await sqlite.sql_get_tests_subjects()
    text = []
    callback = []
    for subject in subjects:
        text.append(subject[0])
        callback.append('tests_'+subject[0])
    text.append('« Назад')
    callback.append('menu')
    pattern = {
        "caption": (
            "<b>📄 Пробники</b>\n"
            "\n"
            "-Выберите предмет"
        ),
        "reply_markup": inline_builder(text=text, callback_data=callback, sizes=1)
    }
    await query.message.edit_caption(**pattern)
    await query.answer()

@router.callback_query(F.data.startswith('tests_'))
async def tests(query: types.CallbackQuery):
    tests = await sqlite.sql_get_tests(query.data.split(sep="_", maxsplit=1)[1])
    buttons = []
    for test in tests:
        buttons.append({'text':test[3], 'callback_data':'test_'+test[3]})
    additional_buttons = [
        [
            types.InlineKeyboardButton(text='« Назад', callback_data="tests"),
        ],
    ]
    paginator = KeyboardPaginator(
        data=buttons,
        router=router,
        per_page=5,
        per_row=1,
        additional_buttons=additional_buttons
    )
    pattern = {
        "caption": (
            "<b>📄 Пробники</b>\n"
            "\n"
        ),
        "reply_markup": paginator.as_markup()
    }
    await query.message.edit_caption(**pattern)
    await query.answer()

@router.callback_query(F.data.startswith('test_'))
async def test(query: types.CallbackQuery):
    test = await sqlite.sql_get_test(query.data.replace('test_', ''))
    pattern = {
        "caption": (
            "<b>"+test[1]+"</b>\n"
            "\n"
            "📄 "+test[2]
        ),
        "reply_markup": inline_builder(text='« Назад', callback_data='delete', sizes=1),
        "document": test[0]
    }
    await query.message.answer_document(**pattern)
    await query.answer()

@router.callback_query(F.data == "delete")
async def delete(query: types.CallbackQuery):
    await query.message.delete()

@router.callback_query(F.data == "menu")
async def menu(query: types.CallbackQuery, isAdmin: bool):
    
    kb = main_kb.inlineKb(isAdmin)
    await query.message.edit_caption(caption="", reply_markup=kb)
    await query.answer()

@router.callback_query(F.data == 'cancel')
async def cancel(query: types.CallbackQuery, state: FSMContext):
    photo = get_project_root('assets/logo.png')
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await query.message.answer_photo(photo=types.FSInputFile(path=photo), caption='Отмена тестирования', reply_markup=inline_builder(text='« Меню', callback_data='menu'))