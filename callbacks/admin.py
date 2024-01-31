from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import types, Router, F
from aiogram.filters import and_f, or_f

from database import sqlite

from filters import IsAdmin, IsGroup

from utils import get_project_root, react_to_post, KeyboardPaginator

import config

from keyboards import inline_builder

router = Router()

class FMStests(StatesGroup):
    file = State()
    subject = State()
    name = State()
    id = State()

class FMSmaterials(StatesGroup):
    photo = State()
    subject = State()
    name = State()
    id = State()

class FMStips(StatesGroup):
    photo = State()
    content = State()

class FMSquestion(StatesGroup):
    photo = State()
    answer = State()
    subject = State()
    title = State()
    explanation = State()

@router.callback_query(and_f(IsAdmin(), F.data == "delete_"))
async def delete(query: types.CallbackQuery):
    pattern = {
        "caption": (
            "<b>❌ Удалить</b>\n"
            "\n"
            "-Выберите данные которые вы хотите удалить"
        ),
        "reply_markup": inline_builder(text=['Удалить тест', 'Удалить материал', '« Назад'], callback_data=['delete_tests', 'delete_materials', 'menu'])
    }
    await query.message.edit_caption(**pattern)
    await query.answer()

@router.callback_query(and_f(IsAdmin(), F.data.startswith('delete_material-')))
async def delete_material(query: types.CallbackQuery):
    await sqlite.sql_delete_material(query.data.split(sep='-', maxsplit=1)[1])
    caption = (
        "<b>Материал был успешно удален</b>"
    )
    await query.message.edit_caption(caption=caption, reply_markup=inline_builder(text=['« Назад'], callback_data=['delete_materials']))
    await query.answer()

@router.callback_query(and_f(IsAdmin(), F.data.startswith('delete_test-')))
async def delete_test(query: types.CallbackQuery):
    await sqlite.sql_delete_test(query.data.split(sep='-', maxsplit=1)[1])
    caption = (
        "<b>Тест был успешно удален</b>"
    )
    await query.message.edit_caption(caption=caption, reply_markup=inline_builder(text=['« Назад'], callback_data=['delete_tests']))
    await query.answer()

@router.callback_query(and_f(IsAdmin(), F.data.startswith("delete")))
async def delete(query: types.CallbackQuery):
    pattern = {}
    if query.data == 'delete_tests':
        tests = await sqlite.sql_get_tests(None)
        buttons = []
        pattern['caption'] = (
            "<b>❌ Удалить тест</b>\n"
            "\n"
            "-Выберите тест для удаления"
        )
        buttons = []
        for test in tests:
            buttons.append({'text':test[3], 'callback_data':'delete_test-'+test[3]})
        additional_buttons = [
            [
                types.InlineKeyboardButton(text='« Назад', callback_data="delete_"),
            ],
        ]
        paginator = KeyboardPaginator(
            data=buttons,
            router=router,
            per_page=5,
            per_row=1,
            additional_buttons=additional_buttons
        )
        pattern['reply_markup'] = paginator.as_markup()
        await query.message.edit_caption(**pattern)
        await query.answer()
    if query.data == 'delete_materials':
        materials = await sqlite.sql_get_materials(None)
        pattern['caption'] = (
            "<b>❌ Удалить материал</b>\n"
            "\n"
            "-Выберите материал для удаления"
        )
        buttons = []
        for material in materials:
            buttons.append({'text':material[3], 'callback_data':'delete_material-'+material[3]})
        additional_buttons = [
            [
                types.InlineKeyboardButton(text='« Назад', callback_data="delete_"),
            ],
        ]
        paginator = KeyboardPaginator(
            data=buttons,
            router=router,
            per_page=5,
            per_row=1,
            additional_buttons=additional_buttons
        )
        pattern['reply_markup'] = paginator.as_markup()
        await query.message.edit_caption(**pattern)
        await query.answer()

@router.callback_query(and_f(IsAdmin(), F.data == "post"))
async def post(query: types.CallbackQuery):
    pattern = {
        "caption": (
            "<b>✔ Выложить</b>\n"
            "\n"
            "-Выберите данные которые вы хотите выложить"
        ),
        "reply_markup": inline_builder(text=['Выложить тест', 'Выложить материал', 'Выложить совет', 'Выложить вопрос', '« Назад'], callback_data=['post_tests', 'post_materials', 'post_tips', 'post_question', 'menu'])
    }
    await query.message.edit_caption(**pattern)
    await query.answer()


@router.callback_query(and_f(IsAdmin(), F.data.startswith('post_test-')))
async def post_test(query: types.CallbackQuery):
    test = await sqlite.sql_get_test(query.data.split(sep='-', maxsplit=1)[1])
    caption = (
        "<b>"+test[1]+"</b>\n"
        "\n"
        "#пробники #"+test[2]
    )
    mes = await query.bot.send_document(chat_id=config.channel, document=test[0], caption=caption)
    await react_to_post(message=mes, emoji=None)
    await query.answer()

@router.callback_query(and_f(IsAdmin(), F.data.startswith('post_material-')))
async def post_material(query: types.CallbackQuery):
    material = await sqlite.sql_get_material(query.data.split(sep='-', maxsplit=1)[1])
    caption = (
        "<b>"+material[1]+"</b>\n"
        "\n"
        "#материал #"+material[2]
    )
    mes = await query.bot.send_photo(chat_id=config.channel, photo=material[0], caption=caption)
    await react_to_post(message=mes, emoji=None)
    await query.answer()

@router.callback_query(and_f(IsAdmin(), F.data.startswith('post')))
async def post(query: types.CallbackQuery, state: FSMContext):
    pattern = {}
    if query.data == 'post_tests':
        tests = await sqlite.sql_get_tests(None)
        pattern['caption'] = (
            "<b>✔ Выложить тест</b>"
        )
        buttons = []
        for test in tests:
            buttons.append({'text':test[3], 'callback_data':'post_test-'+test[3]})
        additional_buttons = [
            [
                types.InlineKeyboardButton(text='« Назад', callback_data="post"),
            ],
        ]
        paginator = KeyboardPaginator(
            data=buttons,
            router=router,
            per_page=5,
            per_row=1,
            additional_buttons=additional_buttons
        )
        pattern['reply_markup'] = paginator.as_markup()
        await query.message.edit_caption(**pattern)
        await query.answer()
    if query.data == 'post_materials':
        materials = await sqlite.sql_get_materials(None)
        pattern['caption'] = (
            "<b>✔ Выложить материал</b>"
        )
        buttons = []
        for material in materials:
            buttons.append({'text':material[3], 'callback_data':'post_material-'+material[3]})
        additional_buttons = [
            [
                types.InlineKeyboardButton(text='« Назад', callback_data="post"),
            ],
        ]
        paginator = KeyboardPaginator(
            data=buttons,
            router=router,
            per_page=5,
            per_row=1,
            additional_buttons=additional_buttons
        )
        pattern['reply_markup'] = paginator.as_markup()
        await query.message.edit_caption(**pattern)
        await query.answer()
    if query.data == 'post_tips':
        pattern['caption'] = (
            "<b>✔ Выложить совет</b>"
        )
        pattern['reply_markup'] = inline_builder(text=['« Назад'], callback_data=['post'], sizes=1)
        await query.message.edit_caption(**pattern)
        await query.message.answer('Загрузите фото', reply_markup=inline_builder(text='« Отменить', callback_data='cancel'))
        await state.set_state(FMStips.photo)
    if query.data == 'post_question':
        pattern['caption'] = (
            "<b>✔ Выложить вопрос</b>"
        )
        pattern['reply_markup'] = inline_builder(text=['« Назад'], callback_data=['post'], sizes=1)
        await query.message.edit_caption(**pattern)
        await query.message.answer('Загрузите фото', reply_markup=inline_builder(text='« Отменить', callback_data='cancel'))
        await state.set_state(FMSquestion.photo)

@router.message(and_f(IsAdmin(), F.content_type == 'photo', FMSquestion.photo))
async def add_question_photo(message: types.Message, state: FSMContext):
    await state.update_data(photo=message.photo[0].file_id)
    await message.answer('Теперь введите текст', reply_markup=inline_builder(text='« Отменить', callback_data='cancel'))
    await state.set_state(FMSquestion.title)

@router.message(and_f(IsAdmin(), F.content_type == 'text', FMSquestion.title))
async def add_question_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.html_text)
    await message.answer('Теперь введите предмет', reply_markup=inline_builder(text='« Отменить', callback_data='cancel'))
    await state.set_state(FMSquestion.subject)

@router.message(and_f(IsAdmin(), F.content_type == 'text', FMSquestion.subject))
async def add_question_subject(message: types.Message, state: FSMContext):
    await state.update_data(subject=message.text)
    await message.answer('Теперь введите ответ', reply_markup=inline_builder(text='« Отменить', callback_data='cancel'))
    await state.set_state(FMSquestion.answer)

@router.message(and_f(IsAdmin(), F.content_type == 'text', FMSquestion.answer))
async def add_question_answer(message: types.Message, state: FSMContext):
    await state.update_data(answer=message.html_text)
    await message.answer('Теперь введите объяснение', reply_markup=inline_builder(text='« Отменить', callback_data='cancel'))
    await state.set_state(FMSquestion.explanation)

@router.message(or_f(IsGroup(), and_f(IsAdmin(), F.content_type == 'text', FMSquestion.explanation)))
async def add_question_explanation(message: types.Message, state: FSMContext):    
    photo = get_project_root('assets/logo.png')
    global data
    if message.chat.type in ['supergroup'] and message.from_user.id == 777000:
        try:
            caption = (
                "Ответ: "+data['answer']+"\n"
                "\n"
                ""+data['explanation']
            )
            await message.reply(caption)
            del data['answer']
            del data['explanation']
            await state.clear()
        except KeyError:
            await state.clear()
        except NameError:
            await state.clear()
    else:
        await message.answer_photo(photo=types.FSInputFile(path=photo) ,caption='Вопрос был успешно выложен', reply_markup=inline_builder(text='« Меню', callback_data='menu'))
        await state.update_data(explanation=message.html_text)
        data = await state.get_data()
        caption = (
            data['title']+"\n"
            "\n"
            "#вопросы #"+data['subject']
        )
        mes = await message.bot.send_photo(chat_id=config.channel ,photo=data['photo'], caption=caption)
        await react_to_post(message=mes, emoji=None)

@router.message(and_f(IsAdmin(), F.content_type == 'photo', FMStips.photo))
async def add_tips_photo(message: types.Message, state: FSMContext):
    await state.update_data(photo=message.photo[0].file_id)
    await message.answer('Теперь введите текст', reply_markup=inline_builder(text='« Отменить', callback_data='cancel'))
    await state.set_state(FMStips.content)

@router.message(and_f(IsAdmin(), F.content_type == 'text', FMStips.content))
async def add_tips_content(message: types.Message, state: FSMContext):
    photo = get_project_root('assets/logo.png')
    await state.update_data(content=message.html_text)
    data = await state.get_data()
    await message.answer_photo(photo=types.FSInputFile(path=photo) ,caption='Совет был успешно выложен', reply_markup=inline_builder(text='« Меню', callback_data='menu'))
    caption = (
        data['content']+"\n"
        "\n"
        "#советы"
    )
    mes = await message.bot.send_photo(chat_id=config.channel ,photo=data['photo'], caption=caption)
    await react_to_post(message=mes, emoji=None)
    await state.clear()

@router.callback_query(and_f(IsAdmin(), F.data == "add"))
async def add(query: types.CallbackQuery):
    pattern = {
        "caption": (
            "<b>✅ Добавить</b>\n"
            "\n"
            "-Выберите данные которые вы хотите добавить"
        ),
        "reply_markup": inline_builder(text=['Добавить тест', 'Добавить материал', '« Назад'], callback_data=['add_tests', 'add_materials', 'menu'])
    }
    await query.message.edit_caption(**pattern)
    await query.answer()

@router.callback_query(and_f(IsAdmin(), F.data.startswith('add')))
async def add(query: types.CallbackQuery, state: FSMContext):
    if query.data == 'add_tests':
        await query.message.answer('Загрузите файл', reply_markup=inline_builder(text='« Отменить', callback_data='cancel'))
        await state.set_state(FMStests.file)
    if query.data == 'add_materials':
        await query.message.answer('Загрузите фото', reply_markup=inline_builder(text='« Отменить', callback_data='cancel'))
        await state.set_state(FMSmaterials.photo)

@router.message(and_f(IsAdmin(), F.content_type == 'document', FMStests.file))
async def add_tests_file(message: types.Message, state: FSMContext):
    await state.update_data(file=message.document.file_id)
    await message.answer('Теперь введите название', reply_markup=inline_builder(text='« Отменить', callback_data='cancel'))
    await state.set_state(FMStests.name)

@router.message(and_f(IsAdmin(), F.content_type == 'text', FMStests.name))
async def add_tests_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Теперь введите предмет', reply_markup=inline_builder(text='« Отменить', callback_data='cancel'))
    await state.set_state(FMStests.subject)

@router.message(and_f(IsAdmin(), F.content_type == 'text', FMStests.subject))
async def add_tests_id(message: types.Message, state: FSMContext):
    await state.update_data(subject=message.text)
    await message.answer('Теперь введите id', reply_markup=inline_builder(text='« Отменить', callback_data='cancel'))
    await state.set_state(FMStests.id)

@router.message(and_f(IsAdmin(), F.content_type == 'text', FMStests.id))
async def add_tests_subject(message: types.Message, state: FSMContext):
    photo = get_project_root('assets/logo.png')
    await state.update_data(id=message.text)
    await sqlite.sql_add_tests(state)
    await state.clear()
    await message.answer_photo(photo=types.FSInputFile(path=photo), caption='Тест был успешно добавлен', reply_markup=inline_builder(text='« Меню', callback_data='menu'))

@router.message(and_f(IsAdmin(), F.content_type == 'photo', FMSmaterials.photo))
async def add_materials_photo(message: types.Message, state: FSMContext):
    await state.update_data(photo=message.photo[0].file_id)
    await message.answer('Теперь введите название', reply_markup=inline_builder(text='« Отменить', callback_data='cancel'))
    await state.set_state(FMSmaterials.name)

@router.message(and_f(IsAdmin(), F.content_type == 'text', FMSmaterials.name))
async def add_materials_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Теперь введите предмет', reply_markup=inline_builder(text='« Отменить', callback_data='cancel'))
    await state.set_state(FMSmaterials.subject)

@router.message(and_f(IsAdmin(), F.content_type == 'text', FMSmaterials.subject))
async def add_materials_subject(message: types.Message, state: FSMContext):
    await state.update_data(subject=message.text)
    await message.answer('Теперь введите id', reply_markup=inline_builder(text='« Отменить', callback_data='cancel'))
    await state.set_state(FMSmaterials.id)
    
@router.message(and_f(IsAdmin(), F.content_type == 'text', FMSmaterials.id))
async def add_materials_id(message: types.Message, state: FSMContext):
    photo = get_project_root('assets/logo.png')
    await state.update_data(id=message.text)
    await sqlite.sql_add_materials(state)
    await state.clear()
    await message.answer_photo(photo=types.FSInputFile(path=photo), caption='Материал был успешно добавлен', reply_markup=inline_builder(text='« Меню', callback_data='menu'))

@router.callback_query(F.data == 'cancel')
async def cancel(query: types.CallbackQuery, state: FSMContext):
    photo = get_project_root('assets/logo.png')
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await query.message.answer_photo(photo=types.FSInputFile(path=photo), caption='Отмена добавления данных', reply_markup=inline_builder(text='« Меню', callback_data='menu'))
