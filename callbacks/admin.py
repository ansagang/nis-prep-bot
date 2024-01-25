from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from database import sqlite
from aiogram import Dispatcher, types
from aiogram import Router, F
from filters import IsAdmin
from aiogram.filters import and_f, or_f, Command
from utils import get_project_root

from keyboards import inline_builder

router = Router()

class FMStests(StatesGroup):
    file = State()
    subject = State()
    name = State()


@router.callback_query(F.data == "add")
async def add(query: types.CallbackQuery):
    pattern = {
        "caption": (
            "<b>Добавить</b>\n"
            "\n"
            "-Выберите данные которые вы хотите добавить"
        ),
        "reply_markup": inline_builder(text=['Добавить тест', 'Добавить материал', 'Добавить совет', '« Назад'], callback_data=['add_tests', 'add_materials', 'add_tips', 'menu'])
    }
    await query.message.edit_caption(**pattern)
    await query.answer()

# @router.message(F.text.startswith('add'))
# async def add(message: types.Message, state: FSMContext):
#     if message.text == 'add_tests':
#         await message.message.reply('Загрузите файл', reply_markup=inline_builder(text='« Отменить', callback_data='menu'))
#         await state.set_state(FMStests.file)

@router.callback_query(F.data.startswith('add'))
async def add(query: types.CallbackQuery, state: FSMContext):
    if query.data == 'add_tests':
        await query.message.answer('Загрузите файл', reply_markup=inline_builder(text='« Отменить', callback_data='cancel'))
        await state.set_state(FMStests.file)

@router.message(and_f(IsAdmin(), F.content_type == 'document', FMStests.file))
async def add(message: types.Message, state: FSMContext):
    await state.update_data(file=message.document.file_id)
    await message.answer('Теперь введите название', reply_markup=inline_builder(text='« Отменить', callback_data='cancel'))
    await state.set_state(FMStests.name)

@router.message(and_f(IsAdmin(), F.content_type == 'text', FMStests.name))
async def add(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Теперь введите предмет', reply_markup=inline_builder(text='« Отменить', callback_data='cancel'))
    await state.set_state(FMStests.subject)

@router.message(and_f(IsAdmin(), F.content_type == 'text', FMStests.subject))
async def add(message: types.Message, state: FSMContext):
    photo = get_project_root('assets/logo.png')
    await state.update_data(subject=message.text)
    await sqlite.sql_add_tests(state)
    await state.clear()
    await message.answer_photo(photo=types.FSInputFile(path=photo), caption='Тест был успешно добавлен', reply_markup=inline_builder(text='« Меню', callback_data='menu'))

@router.callback_query(F.data == 'cancel')
async def add(query: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await query.message.answer('Отмена добавления данных')

