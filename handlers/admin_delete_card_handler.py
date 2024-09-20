from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


from config_data.config import Config, load_config
from keyboards.admin_delete_card_keyboard import create_keyboard_list, keyboard_confirm_delete_card

from database import requests as rq
from filter.admin_filter import IsSuperAdmin


import logging

router = Router()
router.message.filter(IsSuperAdmin())
router.callback_query(IsSuperAdmin())
config: Config = load_config()


class Admin(StatesGroup):
    category_card = State()


@router.message(F.text == '❌ Удалить карточку')
async def process_add_card(message: Message) -> None:
    """
    Запускаем функционал удаления карточки заведения
    :param message:
    :return:
    """
    logging.info(f'process_add_card: {message.chat.id}')
    list_category = await rq.get_list_category()
    await message.answer(text=f'Выберите категорию заведение, из которого нужно удалить',
                         reply_markup=create_keyboard_list(list_name_button=list_category,
                                                           str_callback='deletecategory'))


@router.callback_query(F.data.startswith('deletecategory'))
async def process_select_category_card(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Получаем категорию для удаления
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_select_category_card: {callback.message.chat.id}')
    list_subcategory = await rq.get_list_subcategory(callback.data.split(':')[1])
    await state.update_data(category=callback.data.split(':')[1])
    if list_subcategory != ['none']:
        await callback.message.edit_text(text=f'Выберите подкатегорию места для удаления',
                                         reply_markup=create_keyboard_list(list_name_button=list_subcategory,
                                                                           str_callback='deletesubcategory'))
    else:
        list_card = await rq.get_list_card(category=callback.data.split(':')[1], sub_category='none')
        list_title_card = []
        list_id_card = []
        for card in list_card:
            list_title_card.append(card["title"])
            list_id_card.append(card["id_place"])
        await callback.message.edit_text(text='Выберите заведение для удаления',
                                         reply_markup=create_keyboard_list(list_name_button=list_title_card,
                                                                           str_callback='title_card',
                                                                           list_id_button=list_id_card))
    await callback.answer()


@router.callback_query(F.data.startswith('deletesubcategory'))
async def process_select_category_card(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Получаем подкатегорию заведения для удаления
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_select_category_card: {callback.message.chat.id}')
    await state.update_data(subcategory=callback.data.split(':')[1])
    data = await state.get_data()
    list_card = await rq.get_list_card(data['category'],
                                       data['subcategory'])
    list_title_card = []
    list_id_card = []
    for card in list_card:
        list_title_card.append(card["title"])
        list_id_card.append(card["id_place"])
    await callback.message.edit_text(text='Выберите заведение для удаления',
                                     reply_markup=create_keyboard_list(list_name_button=list_title_card,
                                                                       str_callback='title_card',
                                                                       list_id_button=list_id_card))
    await callback.answer()


@router.callback_query(F.data.startswith('title_card'))
async def process_select_title_card(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Получаем заведение для удаления
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_select_title_card: {callback.message.chat.id}')
    await state.update_data(id_title=callback.data.split(":")[1])
    card = await rq.info_card(int(callback.data.split(":")[1]))
    await callback.message.edit_text(text=f'Вы точно хотите удалить <b>{card.title}</b>',
                                     reply_markup=keyboard_confirm_delete_card(),
                                     parse_mode='html')
    await callback.answer()


@router.callback_query(F.data == 'yes_delete')
async def process_yes_delete_title_card(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Удаление подтверждено
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_yes_delete_title_card: {callback.message.chat.id}')
    data = await state.get_data()
    card = await rq.info_card(int(data['id_title']))
    await rq.delete_card(id_place=data['id_title'])
    await callback.message.edit_text(text=f'Заведение {card.title} успешно удалено',
                                     reply_markup=None)
    await callback.answer()


@router.callback_query(F.data == 'no_delete')
async def process_yes_delete_title_card(callback: CallbackQuery) -> None:
    """
    Отмена удаления карточки заведения
    :param callback:
    :return:
    """
    logging.info(f'process_yes_delete_title_card: {callback.message.chat.id}')
    await callback.message.edit_text(text='Удаление отменено',
                                     reply_markup=None)
    await callback.answer()
