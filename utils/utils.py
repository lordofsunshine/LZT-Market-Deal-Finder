from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from aiogram.exceptions import TelegramBadRequest


async def safe_edit_text(msg: Message, text: str, markup: InlineKeyboardMarkup = None, parse_mode: str = "HTML"):
    try:
        await msg.edit_text(text=text, reply_markup=markup, parse_mode=parse_mode)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise e


async def safe_edit_markup(msg: Message, markup: InlineKeyboardMarkup):
    try:
        await msg.edit_reply_markup(reply_markup=markup)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise e


async def safe_callback_edit_text(cb: CallbackQuery, text: str, markup: InlineKeyboardMarkup = None, parse_mode: str = "HTML"):
    try:
        await cb.message.edit_text(text=text, reply_markup=markup, parse_mode=parse_mode)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise e


async def safe_callback_edit_markup(cb: CallbackQuery, markup: InlineKeyboardMarkup):
    try:
        await cb.message.edit_reply_markup(reply_markup=markup)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise e
