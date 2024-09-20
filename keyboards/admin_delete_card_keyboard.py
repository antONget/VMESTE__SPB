from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging
import validators


def create_keyboard_list(list_name_button: list, str_callback: str, list_id_button: list = []):
    logging.info("create_keyboard_list")
    kb_builder = InlineKeyboardBuilder()
    list_button = []
    if list_id_button == []:
        for i, value in enumerate(list_name_button):
            list_button.append(InlineKeyboardButton(text=value, callback_data=f'{str_callback}:{value}'))
    else:
        for i, value in enumerate(list_name_button):
            # if 'Мероприятия недели' in value:
            #     continue
            list_button.append(InlineKeyboardButton(text=value, callback_data=f'{str_callback}:{list_id_button[i]}'))
    # Распаковываем список с кнопками в билдер методом row c параметром width
    kb_builder.row(*list_button, width=1)
    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()


def keyboard_confirm_delete_card():
    logging.info("keyboard_get_more")
    button_1 = InlineKeyboardButton(text='Нет',  callback_data=f'no_delete')
    button_2 = InlineKeyboardButton(text='Да', callback_data=f'yes_delete')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]], )
    return keyboard