from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging
import validators


def create_keyboard_list(list_name_button, str_callback, list_id_button: list = []):
    """
    Клавиатура формируется по заданному списку, а для подкатегорий м карточек также добавляет кнопку "Поднять в ТОП"
    :param list_name_button:
    :param str_callback:
    :param list_id_button:
    :return:
    """
    logging.info(f"create_keyboard_list, {str_callback}")
    kb_builder = InlineKeyboardBuilder()
    list_button = []
    if str_callback == 'editsubcategory':
        list_button.append(InlineKeyboardButton(text='Поднять в TOP', callback_data=f'top_category'))
    elif str_callback == 'edittitle_card':
        list_button.append(InlineKeyboardButton(text='Поднять в TOP', callback_data=f'top_sub_category'))
    if list_id_button == []:
        for i, value in enumerate(list_name_button):
            # if 'Мероприятия недели' in value:
            #     continue
            list_button.append(InlineKeyboardButton(text=value, callback_data=f'{str_callback}:{value}'))
    else:
        for i, value in enumerate(list_name_button):
            list_button.append(InlineKeyboardButton(text=value, callback_data=f'{str_callback}:{list_id_button[i]}'))
    # Распаковываем список с кнопками в билдер методом row c параметром width
    kb_builder.row(*list_button, width=1)
    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()


def keyboard_details_edit(id_card):
    logging.info("keyboard_details")
    button_1 = InlineKeyboardButton(text='Узнать больше',  callback_data=f'details_edit:{id_card}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]], )
    return keyboard


def keyboards_edit_attribute():
    logging.info("keyboards_start_admin")
    button_0 = KeyboardButton(text='Категория')
    button_1 = KeyboardButton(text='Название')
    button_3 = KeyboardButton(text='Короткое описание')
    button_4 = KeyboardButton(text='Полное описание')
    button_5 = KeyboardButton(text='Адрес')
    button_top = KeyboardButton(text='Поднять в TOP')
    button_6 = KeyboardButton(text='Главное меню')
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_0], [button_1], [button_3], [button_4], [button_5], [button_top], [button_6]],
        resize_keyboard=True
    )
    return keyboard


def keyboard_confirm_delete_card():
    logging.info("keyboard_get_more")
    button_1 = InlineKeyboardButton(text='Нет',  callback_data=f'no_edit')
    button_2 = InlineKeyboardButton(text='Да', callback_data=f'yes_edit')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]], )
    return keyboard


def keyboard_full_text(yandex, instagram):
    logging.info("keyboard_full_text")
    button_1 = ''
    button_2 = ''
    if validators.url(yandex):
        button_1 = InlineKeyboardButton(text='Яндекс Карты',  url=f'{yandex}')
    else:
        button_1 = InlineKeyboardButton(text='Яндекс Карты', callback_data=' ')
    if validators.url(instagram):
        button_2 = InlineKeyboardButton(text='Ссылка на проект',  url=f'{instagram}')
    else:
        button_2 = InlineKeyboardButton(text='Ссылка на проект', callback_data=' ')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1, button_2]], )
    return keyboard


def keyboard_full_text_1(yandex):
    logging.info("keyboard_full_text_1")
    button_1 = ''
    if validators.url(yandex):
        button_1 = InlineKeyboardButton(text='Яндекс Карты',  url=f'{yandex}')
    else:
        button_1 = InlineKeyboardButton(text='Яндекс Карты', callback_data=' ')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]], )
    return keyboard
