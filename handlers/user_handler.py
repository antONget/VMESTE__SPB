from aiogram import Router, F
from aiogram.filters import CommandStart, or_f, and_f
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


from keyboards.user_keyboards import keyboards_start_user, create_keyboard_list, keyboard_details, keyboard_full_text, \
    keyboard_full_text_1, keyboard_get_more, keyboard_get_more_event
from filter.admin_filter import IsSuperAdmin
from config_data.config import Config, load_config
from database import requests as rq
from database.models import Place

import logging
router = Router()
# Загружаем конфиг в переменную config
config: Config = load_config()


class User(StatesGroup):
    category = State()


@router.message(or_f(and_f(CommandStart(), ~IsSuperAdmin()),
                     and_f(IsSuperAdmin(), F.text == '/user')))
async def process_start_command_user(message: Message, state: FSMContext) -> None:
    """
    Пользовательский режим запускается если, пользователь ввел команду /start
     или если администратор ввел команду /user
    1. Добавляем пользователя в БД если его еще нет в ней
    :param message:
    :param state:
    :return:
    """
    logging.info(f'process_start_command_user: {message.chat.id}')
    await state.update_data(state=None)
    await rq.add_user(tg_id=message.chat.id,
                      data={"tg_id": message.chat.id, "username": message.from_user.username})
    await message.answer(text=f'Привет, друг/подружка!\n\n'
                              f'Это дружеское медиа по городам Вместе, созданное командой подружек!\n\n'
                              f'Что ты найдешь здесь?\n'
                              f'🪩где вкусно поесть или выпить: рестораны, бары, кофейни на любой вкус \n'
                              f'🌲куда уехать загород\n'
                              f'☀️каким спортом заняться или в каком спа отдохнуть\n'
                              f'🦪винтажные споты и стильные магазины\n'
                              f'🐚недорогие заведения отели и домики\n\n'
                              f'📍любой проект ты найдешь на Яндекс.картах, чтобы было удобно построить маршрут\n\n'
                              f'По вопросам размещения вашего проекта в боте свяжитесь с Никой @legeau',
                         reply_markup=keyboards_start_user())


@router.message(F.text == 'Выбрать место')
async def process_start_command_user(message: Message) -> None:
    """
    Вывод списка категорий мест для выбора
    :param message:
    :return:
    """
    logging.info(f'process_start_command_user: {message.chat.id}')
    list_category: list = await rq.get_list_category()
    await message.answer(text=f'Выберите категорию места',
                         reply_markup=create_keyboard_list(list_name_button=list_category,
                                                           str_callback='usercategory'))


async def show_card(callback: CallbackQuery, state: FSMContext, list_card: list) -> None:
    """
    Функция отображения карточек мест
    :param callback:
    :param state:
    :param list_card:
    :return:
    """
    logging.info(f'process_select_category_card: {callback.message.chat.id}')
    count_show = 3
    data = await state.get_data()
    count_card_show = data['count_card_show'] + count_show
    await state.update_data(count_card_show=count_card_show)
    for info_card in list_card[count_card_show - count_show:count_card_show]:
        media = []
        list_image = info_card["list_image"].split(',')
        for image in list_image:
            media.append(InputMediaPhoto(media=image))
        await callback.message.answer_media_group(media=media)
        await callback.message.answer(text=f'<b>{info_card["title"]}</b>\n'
                                           f'{info_card["short_description"]}',
                                      reply_markup=keyboard_details(info_card["id_place"]),
                                      parse_mode='html')
    if len(list_card) > count_card_show:
        await callback.message.answer(text='Не хватило мест?',
                                      reply_markup=keyboard_get_more())


@router.callback_query(F.data == 'get_more')
async def process_select_get_more(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Показываем еще 3 карточки
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_select_get_more: {callback.message.chat.id}')
    data = await state.get_data()
    list_card = data['list_card']
    await show_card(callback=callback, state=state, list_card=list_card)


@router.callback_query(F.data.startswith('usercategory'))
async def process_select_category_card(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Выбранная пользователем категория
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_select_category_card: {callback.message.chat.id}')
    list_subcategory = await rq.get_list_subcategory(callback.data.split(':')[1])
    await state.update_data(category=callback.data.split(':')[1])
    print(list_subcategory)
    # если у категории есть подкатегории
    if list_subcategory != ['none']:
        await callback.message.edit_text(text=f'Выберите подкатегорию места',
                                         reply_markup=create_keyboard_list(list_name_button=list_subcategory,
                                                                           str_callback='usersubcategory'))
    # иначе отображаем карточки мест выбранной категории
    else:
        await callback.message.answer(text=f'Подкатегорий у категории нет')
        await state.update_data(subcategory='none')
        data = await state.get_data()
        list_card = await rq.get_list_card(data['category'],
                                           data['subcategory'])
        await state.update_data(list_card=list_card)
        await state.update_data(count_card_show=0)
        await show_card(callback=callback, state=state, list_card=list_card)
    await callback.answer()


@router.callback_query(F.data.startswith('usersubcategory'))
async def process_select_category_card(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Отображаем карточки мест выбранной подкатегории
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_select_category_card: {callback.message.chat.id}')
    await state.update_data(subcategory=callback.data.split(':')[1])
    data = await state.get_data()
    list_card = await rq.get_list_card(data['category'],
                                       data['subcategory'])
    await state.update_data(list_card=list_card)
    await state.update_data(count_card_show=0)
    logging.info(f'process_select_category_card: {callback.message.chat.id}')
    await show_card(callback=callback, state=state, list_card=list_card)


@router.callback_query(F.data.startswith('details_user:'))
async def process_details(callback: CallbackQuery) -> None:
    """
    Действия
    :param callback:
    :return:
    """
    logging.info(f'process_details: {callback.message.chat.id}')
    id_card = callback.data.split(':')[1]
    card = await rq.info_card(int(id_card))
    count = card.count_link + 1
    await rq.set_count_show_card(count=count, id_card=id_card)
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


async def show_card_event(message: Message, state: FSMContext, list_event: list[Place]) -> None:
    """
    Показать карточки мероприятий
    :param message:
    :param state:
    :param list_event:
    :return:
    """
    logging.info(f'show_card_event: {message.chat.id}')
    count_show = 3
    data = await state.get_data()
    count_event_show = data['count_event_show'] + count_show
    await state.update_data(count_event_show=count_event_show)
    for info_event in list_event[count_event_show - count_show:count_event_show]:
        media = []
        list_image = info_event.list_image.split(',')
        for image in list_image:
            media.append(InputMediaPhoto(media=image))
        await message.answer_media_group(media=media)
        await message.answer(text=f'<b>{info_event.title}</b>\n{info_event.short_description}',
                             reply_markup=keyboard_details(info_event.id_place),
                             parse_mode='html')
    if len(list_event) > count_event_show:
        await message.answer(text='Не хватило мест?',
                             reply_markup=keyboard_get_more_event())


@router.message(F.text == '🎧Мероприятия недели')
async def process_events_week(message: Message, state: FSMContext) -> None:
    """
    Выбрана категория Мероприятия
    :param message:
    :param state:
    :return:
    """
    logging.info(f'process_events_week: {message.chat.id}')
    list_event: list = await rq.get_list_card_event()
    await state.update_data(list_event=list_event)
    await state.update_data(count_event_show=0)
    await show_card_event(message=message, state=state, list_event=list_event)


@router.callback_query(F.data == 'get_more_event')
async def process_select_get_more_event(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Показать больше информации о мероприятии
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_select_get_more_event: {callback.message.chat.id}')
    data = await state.get_data()
    list_event = data['list_event']
    await show_card_event(message=callback.message, state=state, list_event=list_event)


@router.callback_query(F.data.startswith('event_'))
async def process_event_show(callback: CallbackQuery) -> None:
    logging.info(f'process_event_show: {callback.message.chat.id}')
    info_event = await rq.info_card(id_card=int(callback.data.split('_')[1]))
    media = []
    list_image = info_event.list_image.split(',')
    for image in list_image:
        media.append(InputMediaPhoto(media=image))
    await callback.message.answer_media_group(media=media)
    await callback.message.answer(text=f'<b>{info_event.title}</b>\n'
                                       f'{info_event.short_description}',
                                  reply_markup=keyboard_details(info_event.id_place),
                                  parse_mode='html')


@router.message(F.text == 'Задать вопрос')
async def process_question(message: Message) -> None:
    """
    Обработка обратной связи
    :param message:
    :return:
    """
    logging.info(f'process_question: {message.chat.id}')
    await message.answer(text='Если у вас возникли вопросы по работе бота или у вас есть предложения,'
                              ' то можете написать @legeau')
