from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


from config_data.config import Config, load_config
from keyboards.admin_edit_card_keyboard import create_keyboard_list, keyboard_details_edit, keyboards_edit_attribute, \
    keyboard_full_text, keyboard_full_text_1
from keyboards.admin_main_keyboards import keyboards_start_admin

from database import requests as rq
from database.models import Place
from filter.admin_filter import IsSuperAdmin


import logging

router = Router()
router.message.filter(IsSuperAdmin())
router.callback_query(IsSuperAdmin())
config: Config = load_config()


class Admin(StatesGroup):
    update_attribute = State()


@router.message(F.text == '📝 Редактировать карточку')
async def process_edit_card(message: Message, state: FSMContext) -> None:
    """
    Запуск функционала по редактированию карточек мест (выводим список категорий мест)
    :param message:
    :param state:
    :return:
    """
    logging.info(f'process_edit_card: {message.chat.id}')
    await state.clear()
    list_category: list[Place] = await rq.get_list_category()
    await message.answer(text=f'Выберите категорию заведение, из которого нужно изменить',
                         reply_markup=create_keyboard_list(list_name_button=list_category,
                                                           str_callback='editcategory'))


@router.callback_query(F.data == 'top_category')
async def process_top_category(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Устанавливаем позицию категории равной 0, увеличивая значения остальных на 1 (доступна для подкатегорий и заведений)
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_top_category: {callback.message.chat.id} {callback.data}')
    data = await state.get_data()
    await rq.set_position_category(category=data['category'])
    await callback.answer(text='Позиция категории обновлена', show_alert=True)


@router.callback_query(F.data == 'top_sub_category')
async def process_top_sub_category(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Устанавливаем позицию подкатегории равной 0, увеличивая значения остальных на 1
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_top_sub_category: {callback.message.chat.id} {callback.data}')
    data = await state.get_data()
    await rq.set_position_sub_category(category=data['category'], sub_category=data['subcategory'])
    await callback.answer(text=f'Позиция подкатегории {data["subcategory"]} обновлена', show_alert=True)


@router.callback_query(F.data.startswith('editcategory'))
async def process_select_category_card(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обрабатываем нажатие на кнопку "КАТЕГОРИЯ" выводим подкатегории если они есть
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_select_category_card: {callback.message.chat.id}')
    list_subcategory: list[Place] = await rq.get_list_subcategory(callback.data.split(':')[1])
    await state.update_data(category=callback.data.split(':')[1])
    # если список подкатегорий есть
    if list_subcategory != ['none']:
        await callback.message.edit_text(text=f'Выберите подкатегорию места для редактирования',
                                         reply_markup=create_keyboard_list(list_name_button=list_subcategory,
                                                                           str_callback='editsubcategory'))
    # иначе выводи список мест
    else:
        list_card = await rq.get_list_card(category=callback.data.split(':')[1],
                                           sub_category='none')
        list_title_card = []
        list_id_card = []
        for card in list_card:
            list_title_card.append(card["title"])
            list_id_card.append(card["id_place"])
        await callback.message.edit_text(text='Выберите заведение для редактирования',
                                         reply_markup=create_keyboard_list(list_name_button=list_title_card,
                                                                           str_callback='edittitle_card',
                                                                           list_id_button=list_id_card))
    await callback.answer()


@router.callback_query(F.data.startswith('editsubcategory'))
async def process_select_category_card(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обрабатываем нажатие на кнопку "ПОДКАТЕГОРИЯ"
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_select_category_card: {callback.message.chat.id}')
    await state.update_data(subcategory=callback.data.split(':')[1])
    data = await state.get_data()
    list_card: list[Place] = await rq.get_list_card(data['category'],
                                                    data['subcategory'])
    list_title_card = []
    list_id_card = []
    for card in list_card:
        list_title_card.append(card.title)
        list_id_card.append(card.id)
    await callback.message.edit_text(text='Выберите заведение для редактирования',
                                     reply_markup=create_keyboard_list(list_name_button=list_title_card,
                                                                       str_callback='edittitle_card',
                                                                       list_id_button=list_id_card))


@router.callback_query(F.data.startswith('edittitle_card'))
async def process_select_title_card(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обробатываем нажатие на "МЕСТО", выводим карточку МЕСТА и клавиатуру для редактирования ее полей
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_select_title_card: {callback.message.chat.id}')
    await state.update_data(title=callback.data.split(":")[1])
    # получаем информацию о месте по его названию
    card: Place = await rq.info_card(int(callback.data.split(":")[1]))
    await state.update_data(id_card=card.id)
    # формируем контент для карточки
    media = []
    list_image: list = card.list_image.split(',')
    for image in list_image:
        media.append(InputMediaPhoto(media=image))
    await callback.message.answer_media_group(media=media)
    await callback.message.answer(text=f'<b>{card.title}</b>\n'
                                       f'{card.short_description}',
                                  reply_markup=keyboard_details_edit(card.id),
                                  parse_mode='html')
    # клавиатура для выбора действия для редактирования
    await callback.message.answer(text='Выберите поля для редактирования',
                                  reply_markup=keyboards_edit_attribute())


@router.callback_query(F.data.startswith('details_edit:'))
async def process_details(callback: CallbackQuery) -> None:
    """
    Обрабатываем нажатие на кнопку "УЗНАТЬ БОЛЬШЕ", выводим подробную информацию о месте
    :param callback:
    :return:
    """
    logging.info(f'process_details: {callback.message.chat.id}')
    id_card = callback.data.split(':')[1]
    card: Place = await rq.info_card(id_card=int(id_card))
    if card.instagram != 'none':
        await callback.message.edit_text(text=f'<b>{card.title}</b>\n'
                                              f'{card.long_description}\n'
                                              f'<i>{card.address}</i>',
                                         reply_markup=keyboard_full_text(card.yandex_map, card.instagram),
                                         parse_mode='html')
    else:
        await callback.message.edit_text(text=f'<b>{card.title}</b>\n'
                                              f'{card.long_description}\n'
                                              f'<i>{card.address}</i>',
                                         reply_markup=keyboard_full_text_1(card.yandex_map),
                                         parse_mode='html')


@router.message(F.text == 'Главное меню')
async def process_back_menu(message: Message) -> None:
    """
    Обрабатываем нажатие кнопки "ГЛАВНОЕ МЕНЮ", выходим в основное меню бота
    :param message:
    :return:
    """
    logging.info(f'process_back_menu: {message.chat.id}')
    await message.answer(text='Выберите раздел',
                         reply_markup=keyboards_start_admin())


@router.message(lambda message: message.text in ['Название', 'Короткое описание', 'Полное описание', 'Адрес',
                                                 'Категория', 'Поднять в TOP'])
async def process_update_card(message: Message, state: FSMContext) -> None:
    """
    Обработка нажатия кнопки поля которое требуется отредактировать
    :param message:
    :param state:
    :return:
    """
    logging.info(f'process_update_card: {message.chat.id}')
    await state.set_state(Admin.update_attribute)
    await state.update_data(attribute=message.text)
    if message.text == 'Название':
        await message.answer(text='Пришлите новое название:')
    elif message.text == 'Категория':
        await message.answer(text='Пришлите новое название категории:')
    elif message.text == 'Короткое описание':
        await message.answer(text='Пришлите новое короткое описание')
    elif message.text == 'Полное описание':
        await message.answer(text='Пришлите новое полное описание')
    elif message.text == 'Адрес':
        await message.answer(text='Пришлите новый адрес')
    elif message.text == 'Поднять в TOP':
        data = await state.get_data()
        if 'subcategory' not in data.keys():
            await rq.set_position_card(category=data['category'],
                                       sub_category='none',
                                       id_card=int(data['id_card']))
        else:
            await rq.set_position_card(category=data['category'],
                                       sub_category=data['subcategory'],
                                       id_card=int(data['id_card']))
        await message.answer(text='Позиция карточки обновлена')


@router.message(F.text, StateFilter(Admin.update_attribute))
async def process_update_card(message: Message, state: FSMContext) -> None:
    """
    Получаем данные для обновления полей карточки заведения
    :param message:
    :param state:
    :return:
    """
    logging.info(f'process_update_card: {message.chat.id}')
    data = await state.get_data()
    attribute = data['attribute']
    if attribute == 'Название':
        await rq.set_attribute_card(attribute='title',
                                    set_attribute=message.text,
                                    id_card=int(data['id_card']))
        await message.answer(text='Поле обновлено')
    elif attribute == 'Категория':
        await rq.set_attribute_card(attribute='category',
                                    set_attribute=message.text,
                                    id_card=int(data['id_card']))
        await message.answer(text='Поле обновлено')
    elif attribute == 'Короткое описание':
        await rq.set_attribute_card(attribute='short_description',
                                    set_attribute=message.text,
                                    id_card=int(data['id_card']))
        await message.answer(text='Поле обновлено')
    elif attribute == 'Полное описание':
        await rq.set_attribute_card(attribute='long_description',
                                    set_attribute=message.text,
                                    id_card=int(data['id_card']))
        await message.answer(text='Поле обновлено')
    elif attribute == 'Адрес':
        await rq.set_attribute_card(attribute='address',
                                    set_attribute=message.text,
                                    id_card=int(data['id_card']))
        await message.answer(text='Поле обновлено')
