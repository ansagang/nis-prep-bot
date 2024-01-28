from aiogram import Router, F
from aiogram import types

from database import sqlite

from keyboards import inline_builder
from keyboards import main_kb

router = Router()

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
    materials = await sqlite.sql_get_materials(query.data.split('_')[1])
    text = []
    callback = []
    for material in materials:
        text.append(material[3])
        callback.append('material_'+material[3])
    text.append('« Назад')
    callback.append('tests')
    pattern = {
        "caption": (
            "<b>📚 Материалы</b>\n"
            "\n"
        ),
        "reply_markup": inline_builder(text=text, callback_data=callback, sizes=1)
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
    tests = await sqlite.sql_get_tests(query.data.split('_')[1])
    text = []
    callback = []
    for test in tests:
        text.append(test[3])
        callback.append('test_'+test[3])
    text.append('« Назад')
    callback.append('tests')
    pattern = {
        "caption": (
            "<b>📄 Пробники</b>\n"
            "\n"
        ),
        "reply_markup": inline_builder(text=text, callback_data=callback, sizes=1)
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