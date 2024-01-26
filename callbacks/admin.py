from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from database import sqlite
from aiogram import Dispatcher, types
from aiogram import Router, F
from filters import IsAdmin
from aiogram.filters import and_f, or_f, Command
from utils import get_project_root
from database import sqlite
import config

from keyboards import inline_builder

router = Router()

class FMStests(StatesGroup):
    file = State()
    subject = State()
    name = State()

class FMSmaterials(StatesGroup):
    photo = State()
    subject = State()
    name = State()

class FMStips(StatesGroup):
    photo = State()
    content = State()

class FMSquestion(StatesGroup):
    photo = State()
    answer = State()
    subject = State()
    title = State()
    explanation = State()

@router.callback_query(F.data == "post")
async def post(query: types.CallbackQuery):
    pattern = {
        "caption": (
            "<b>Выложить</b>\n"
            "\n"
            "-Выберите данные которые вы хотите выложить"
        ),
        "reply_markup": inline_builder(text=['Выложить тест', 'Выложить материал', 'Выложить совет', 'Выложить вопрос', '« Назад'], callback_data=['post_tests', 'post_materials', 'post_tips', 'post_question', 'menu'])
    }
    await query.message.edit_caption(**pattern)
    await query.answer()


@router.callback_query(F.data.startswith('post_test-'))
async def add(query: types.CallbackQuery):
    test = await sqlite.sql_get_test(query.data.split('-')[1])
    caption = (
        "<b>"+test[1]+"</b>\n"
        "\n"
        "#пробники #"+test[2]
    )
    await query.bot.send_document(chat_id=config.channel, document=test[0], caption=caption)
    await query.answer()

@router.callback_query(F.data.startswith('post_material-'))
async def add(query: types.CallbackQuery):
    material = await sqlite.sql_get_material(query.data.split('-')[1])
    caption = (
        "<b>"+material[1]+"</b>\n"
        "\n"
        "#материал #"+material[2]
    )
    await query.bot.send_photo(chat_id=config.channel, photo=material[0], caption=caption)
    await query.answer()

@router.callback_query(F.data.startswith('post'))
async def add(query: types.CallbackQuery, state: FSMContext):
    pattern = {}
    if query.data == 'post_tests':
        tests = await sqlite.sql_get_tests(None)
        text = []
        callback = []
        pattern['caption'] = (
            "<b>Выложить тест</b>"
        )
        for test in tests:
            text.append(test[1])
            callback.append('post_test-'+test[1])
        text.append('« Назад')
        callback.append('post')
        pattern['reply_markup'] = inline_builder(text=text, callback_data=callback, sizes=1)
        await query.message.edit_caption(**pattern)
        await query.answer()
    if query.data == 'post_materials':
        materials = await sqlite.sql_get_materials(None)
        text = []
        callback = []
        pattern['caption'] = (
            "<b>Выложить материал</b>"
        )
        for material in materials:
            text.append(material[1])
            callback.append('post_material-'+material[1])
        text.append('« Назад')
        callback.append('post')
        pattern['reply_markup'] = inline_builder(text=text, callback_data=callback, sizes=1)
        await query.message.edit_caption(**pattern)
        await query.answer()
    if query.data == 'post_tips':
        pattern['caption'] = (
            "<b>Выложить совет</b>"
        )
        pattern['reply_markup'] = inline_builder(text=['« Назад'], callback_data=['post'], sizes=1)
        await query.message.edit_caption(**pattern)
        await query.message.answer('Загрузите фото', reply_markup=inline_builder(text='« Отменить', callback_data='cancel'))
        await state.set_state(FMStips.photo)
    if query.data == 'post_question':
        pattern['caption'] = (
            "<b>Выложить вопрос</b>"
        )
        pattern['reply_markup'] = inline_builder(text=['« Назад'], callback_data=['post'], sizes=1)
        await query.message.edit_caption(**pattern)
        await query.message.answer('Загрузите фото', reply_markup=inline_builder(text='« Отменить', callback_data='cancel'))
        await state.set_state(FMSquestion.photo)

@router.message(and_f(IsAdmin(), F.content_type == 'photo', FMSquestion.photo))
async def add(message: types.Message, state: FSMContext):
    await state.update_data(photo=message.photo[0].file_id)
    await message.answer('Теперь введите текст', reply_markup=inline_builder(text='« Отменить', callback_data='cancel'))
    await state.set_state(FMSquestion.title)

@router.message(and_f(IsAdmin(), F.content_type == 'text', FMSquestion.title))
async def add(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer('Теперь введите предмет', reply_markup=inline_builder(text='« Отменить', callback_data='cancel'))
    await state.set_state(FMSquestion.subject)

@router.message(and_f(IsAdmin(), F.content_type == 'text', FMSquestion.subject))
async def add(message: types.Message, state: FSMContext):
    await state.update_data(subject=message.text)
    await message.answer('Теперь введите ответ', reply_markup=inline_builder(text='« Отменить', callback_data='cancel'))
    await state.set_state(FMSquestion.answer)

@router.message(and_f(IsAdmin(), F.content_type == 'text', FMSquestion.answer))
async def add(message: types.Message, state: FSMContext):
    await state.update_data(answer=message.text)
    await message.answer('Теперь введите объяснение', reply_markup=inline_builder(text='« Отменить', callback_data='cancel'))
    await state.set_state(FMSquestion.explanation)

@router.message(and_f(IsAdmin(), F.content_type == 'text', FMSquestion.explanation))
async def add(message: types.Message, state: FSMContext):
    photo = get_project_root('assets/logo.png')
    await state.update_data(explanation=message.text)
    data = await state.get_data()
    await message.answer_photo(photo=types.FSInputFile(path=photo) ,caption='Вопрос был успешно выложен', reply_markup=inline_builder(text='« Меню', callback_data='menu'))
    caption = (
        data['title']+"\n"
        "\n"
        "#вопросы #"+data['subject']
    )
    await message.bot.send_photo(chat_id=config.channel ,photo=data['photo'], caption=caption)
    def correct(option):
        if option == 'A':
            return 0
        if option == 'B':
            return 1
        if option == 'C':
            return 2
        if option == 'D':
            return 3
    await message.bot.send_poll(chat_id=config.channel, question='Ответ: ', options=['A', 'B', 'C', 'D'], allows_multiple_answers=False, correct_option_id=correct(data['answer']), explanation=data['explanation'], type='quiz')
    await state.clear()

@router.message(and_f(IsAdmin(), F.content_type == 'photo', FMStips.photo))
async def add(message: types.Message, state: FSMContext):
    await state.update_data(photo=message.photo[0].file_id)
    await message.answer('Теперь введите текст', reply_markup=inline_builder(text='« Отменить', callback_data='cancel'))
    await state.set_state(FMStips.content)

@router.message(and_f(IsAdmin(), F.content_type == 'text', FMStips.content))
async def add(message: types.Message, state: FSMContext):
    photo = get_project_root('assets/logo.png')
    await state.update_data(content=message.text)
    data = await state.get_data()
    await message.answer_photo(photo=types.FSInputFile(path=photo) ,caption='Совет был успешно выложен', reply_markup=inline_builder(text='« Меню', callback_data='menu'))
    caption = (
        data['content']+"\n"
        "\n"
        "#советы"
    )
    await message.bot.send_photo(chat_id=config.channel ,photo=data['photo'], caption=caption)
    await state.clear()

@router.callback_query(F.data == "add")
async def add(query: types.CallbackQuery):
    pattern = {
        "caption": (
            "<b>Добавить</b>\n"
            "\n"
            "-Выберите данные которые вы хотите добавить"
        ),
        "reply_markup": inline_builder(text=['Добавить тест', 'Добавить материал', '« Назад'], callback_data=['add_tests', 'add_materials', 'menu'])
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
    if query.data == 'add_materials':
        await query.message.answer('Загрузите фото', reply_markup=inline_builder(text='« Отменить', callback_data='cancel'))
        await state.set_state(FMSmaterials.photo)

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

@router.message(and_f(IsAdmin(), F.content_type == 'photo', FMSmaterials.photo))
async def add(message: types.Message, state: FSMContext):
    await state.update_data(photo=message.photo[0].file_id)
    await message.answer('Теперь введите название', reply_markup=inline_builder(text='« Отменить', callback_data='cancel'))
    await state.set_state(FMSmaterials.name)

@router.message(and_f(IsAdmin(), F.content_type == 'text', FMSmaterials.name))
async def add(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Теперь введите предмет', reply_markup=inline_builder(text='« Отменить', callback_data='cancel'))
    await state.set_state(FMSmaterials.subject)

@router.message(and_f(IsAdmin(), F.content_type == 'text', FMSmaterials.subject))
async def add(message: types.Message, state: FSMContext):
    photo = get_project_root('assets/logo.png')
    await state.update_data(subject=message.text)
    await sqlite.sql_add_materials(state)
    await state.clear()
    await message.answer_photo(photo=types.FSInputFile(path=photo), caption='Материал был успешно добавлен', reply_markup=inline_builder(text='« Меню', callback_data='menu'))

@router.callback_query(F.data == 'cancel')
async def add(query: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await query.message.answer('Отмена добавления данных')

