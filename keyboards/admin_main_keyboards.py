from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
import logging


def keyboards_start_admin():
    logging.info("keyboards_start_admin")
    button_1 = KeyboardButton(text='➕ Добавить карточку')
    button_3 = KeyboardButton(text='❌ Удалить карточку')
    button_4 = KeyboardButton(text='📝 Редактировать карточку')
    button_5 = KeyboardButton(text='📋 Статистика')
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_1], [button_3], [button_4], [button_5]],
        resize_keyboard=True
    )
    return keyboard
