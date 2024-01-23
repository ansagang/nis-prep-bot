from aiogram import Router, F
from aiogram import types

from keyboards import inline_builder
from keyboards import main_kb

router = Router()


@router.callback_query(F.data == "tips")
async def tips(query: types.CallbackQuery):
    pattern = {
        "caption": (
            "<b>Советы</b>\n"
            "\n"
        ),
        "reply_markup": inline_builder(text='« Назад', callback_data='menu')
    }
    await query.message.edit_caption(**pattern)
    await query.answer()

@router.callback_query(F.data == "materials")
async def tips(query: types.CallbackQuery):
    pattern = {
        "caption": (
            "<b>Материалы</b>\n"
            "\n"
        ),
        "reply_markup": inline_builder(text='« Назад', callback_data='menu')
    }
    await query.message.edit_caption(**pattern)
    await query.answer()

@router.callback_query(F.data == "tests")
async def tips(query: types.CallbackQuery):
    pattern = {
        "caption": (
            "<b>Пробники</b>\n"
            "\n"
        ),
        "reply_markup": inline_builder(text='« Назад', callback_data='menu')
    }
    await query.message.edit_caption(**pattern)
    await query.answer()

@router.callback_query(F.data == "delete")
async def delete(query: types.CallbackQuery):
    await query.message.delete()

@router.callback_query(F.data == "menu")
async def menu(query: types.CallbackQuery, isAdmin: bool):

    kb = main_kb.inlineKb(isAdmin)
    await query.message.edit_caption(caption="", reply_markup=kb)
    await query.answer()