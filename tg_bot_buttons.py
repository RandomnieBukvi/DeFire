from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True,
                           keyboard=[
                               [KeyboardButton(text='Подписаться на устройство')],
                               [KeyboardButton(text='Отписаться от устройства')]
                           ])


def create_inline_markup_from_data(data) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for element in data:
        builder.add(InlineKeyboardButton(
            text=element,
            callback_data=f"delete_device_{element}"
        ))
    return builder.adjust(2).as_markup()
