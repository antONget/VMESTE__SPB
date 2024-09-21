from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


from config_data.config import Config, load_config
from keyboards.admin_add_card_keyboards import create_keyboard_list, keyboard_add_subcategory,\
    keyboards_continue_image, keyboard_add_instagram, keyboard_details, keyboard_full_text, keyboard_full_text_1
from filter.admin_filter import IsSuperAdmin
from database import requests as rq


import logging

router = Router()
router.message.filter(IsSuperAdmin())
router.callback_query(IsSuperAdmin())
config: Config = load_config()


class Admin(StatesGroup):
    category_card = State()
    subcategory_card = State()
    image_card = State()
    title_card = State()
    short_card = State()
    long_card = State()
    address_card = State()
    yandex_card = State()
    instagram_card = State()


@router.message(F.text == '➕ Добавить карточку')
async def process_add_card(message: Message, state: FSMContext) -> None:
    """
    Добавление новой карточки места
    :param message:
    :param state:
    :return:
    """
    logging.info(f'process_add_card: {message.chat.id}')
    list_category = await rq.get_list_category()
    await message.answer(text=f'Введите категорию места или выберите из ранее добавленных',
                         reply_markup=create_keyboard_list(list_name_button=list_category,
                                                           str_callback='category'))
    await state.update_data(image_id_list_image=[])
    await state.set_state(Admin.category_card)


@router.message(F.text, StateFilter(Admin.category_card))
async def process_add_category_card(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Получаем название новой категории. Запрашиваем требуется ли добавить подкатегорию для категории
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_add_category_card: {message.chat.id}')
    await state.set_state(state=None)
    await state.update_data(category_card=message.text)
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id - 1)
    await message.answer(text=f'Добавить подкатегорию для категории {message.text}?',
                         reply_markup=keyboard_add_subcategory())


@router.callback_query(F.data.startswith('category'))
async def process_add_category_card(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Получаем название ранее созданной категории. Запрашиваем требуется ли добавить подкатегорию
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_add_category_card: {callback.message.chat.id}')
    await state.set_state(state=None)
    await state.update_data(category_card=callback.data.split(':')[1])
    await callback.message.edit_text(text=f'Добавить подкатегорию для категории {callback.data.split(":")[1]}?',
                                     reply_markup=keyboard_add_subcategory())
    await callback.answer()


@router.callback_query(F.data == 'yes_subcategory')
async def process_add_subcategory_card(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обрабатываем если у категории есть подкатегория.
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_add_subcategory_card: {callback.message.chat.id}')
    data = await state.update_data()
    list_subcategory = await rq.get_list_subcategory(data["category_card"])
    if list_subcategory != ['none']:
        await callback.message.edit_text(text=f'Введите название подкатегории для категории '
                                              f'{data["category_card"]} или выберите'
                                              f' из списка',
                                         reply_markup=create_keyboard_list(list_name_button=list_subcategory,
                                                                           str_callback='subcategory'))
    else:
        await callback.message.edit_text(text=f'Введите название подкатегории для категории '
                                              f'{data["category_card"]}',
                                         reply_markup=None)
    await state.set_state(Admin.subcategory_card)
    await callback.answer()


@router.callback_query(F.data == 'no_subcategory')
async def process_add_subcategory_card(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обработка если категории нет подкатегории
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_add_nosubcategory_card: {callback.message.chat.id}')
    await state.set_state(state=None)
    await state.update_data(subcategory_card='none')
    await callback.message.edit_text(text=f'Пришлите фотографии заведения',
                                     reply_markup=None)
    await state.set_state(Admin.image_card)
    await callback.answer()


@router.message(F.text, StateFilter(Admin.subcategory_card))
async def process_add_category_card(message: Message, state: FSMContext) -> None:
    """
    Получаем название подкатегории
    :param message:
    :param state:
    :return:
    """
    logging.info(f'process_add_category_card: {message.chat.id}')
    await state.set_state(state=None)
    await state.update_data(subcategory_card=message.text)
    await message.answer(text=f'Пришлите фотографии заведения')
    await state.set_state(Admin.image_card)


@router.callback_query(F.data.startswith('subcategory'))
async def process_add_category_card(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Получаем название ранее добавленной подкатегории
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_add_category_card: {callback.message.chat.id}')
    await state.set_state(state=None)
    await state.update_data(subcategory_card=callback.data.split(':')[1])
    await callback.message.answer(text=f'Пришлите фотографии заведения')
    await state.set_state(Admin.image_card)
    await callback.answer()


@router.message(F.photo, StateFilter(Admin.image_card))
async def get_image_card(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Получаем фотографию для добавления в карточку места
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'get_image_card: {message.chat.id}')
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id - 1)
    image_id = message.photo[-1].file_id
    data = await state.get_data()
    if 'image_id_list_image' in data.keys():
        image_id_list_image = data['image_id_list_image']
        image_id_list_image.append(image_id)
        await state.update_data(image_id_list_image=image_id_list_image)
    else:
        await state.update_data(image_id_list_image=[image_id])
    await message.answer(text='Добавьте еще фото или нажмите «Продолжить».',
                         reply_markup=keyboards_continue_image())


@router.callback_query(F.data == 'continue_image')
async def process_continue_image(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Завершаем добавление фотографий в карточку места
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_continue_image: {callback.message.chat.id}')
    await callback.message.edit_text(text='Введите название места',
                                     reply_markup=None)
    await state.set_state(Admin.title_card)
    await callback.answer()


@router.message(F.text, StateFilter(Admin.title_card))
async def process_get_title_card(message: Message, state: FSMContext) -> None:
    """
    Получаем название заведения
    :param message:
    :param state:
    :return:
    """
    logging.info(f'process_get_title_card: {message.chat.id}')
    await state.set_state(state=None)
    await state.update_data(title_card=message.text.replace('"', ''))
    await message.answer(text=f'Пришлите короткое описание')
    await state.set_state(Admin.short_card)


@router.message(F.text, StateFilter(Admin.short_card))
async def process_get_short_card(message: Message, state: FSMContext) -> None:
    """
    Получаем короткое описание заведения
    :param message:
    :param state:
    :return:
    """
    logging.info(f'process_get_short_card: {message.chat.id}')
    await state.set_state(state=None)
    await state.update_data(short_card=message.text.replace('"', ''))
    await message.answer(text=f'Пришлите полное описание')
    await state.set_state(Admin.long_card)


@router.message(F.text, StateFilter(Admin.long_card))
async def process_get_long_card(message: Message, state: FSMContext) -> None:
    """
    Получаем полное описание заведение
    :param message:
    :param state:
    :return:
    """
    logging.info(f'process_get_long_card: {message.chat.id}')
    await state.set_state(state=None)
    await state.update_data(long_card=message.text.replace('"', ''))
    await message.answer(text=f'Пришлите адрес')
    await state.set_state(Admin.address_card)


@router.message(F.text, StateFilter(Admin.address_card))
async def process_get_address_card(message: Message, state: FSMContext) -> None:
    """
    Получаем адрес заведения
    :param message:
    :param state:
    :return:
    """
    logging.info(f'process_get_address_card: {message.chat.id}')
    await state.set_state(state=None)
    await state.update_data(address_card=message.text.replace('"', ''))
    await message.answer(text=f'Пришлите ссылку на место в яндекс картах')
    await state.set_state(Admin.yandex_card)


@router.message(F.text, StateFilter(Admin.yandex_card))
async def process_get_yandex_card(message: Message, state: FSMContext) -> None:
    """
    Получаем ссылку на яндекс карту
    :param message:
    :param state:
    :return:
    """
    logging.info(f'process_get_yandex_card: {message.chat.id}')
    await state.set_state(state=None)
    await state.update_data(yandex_card=message.text)
    await message.answer(text=f'Есть ссылка на инстаграм?',
                         reply_markup=keyboard_add_instagram())


@router.callback_query(F.data == 'yes_instagram')
async def process_add_instagram_card(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Получаем ссылку на инстаграм
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_add_instagram_card: {callback.message.chat.id}')
    await callback.message.edit_text(text=f'Пришлите ссылку на инстаграм',
                                     reply_markup=None)
    await state.set_state(Admin.instagram_card)
    await callback.answer()


@router.callback_query(F.data == 'no_instagram',)
async def process_add_noinstagram_card(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Обрабатываем нажатие если у заведения нет инстаграмм
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_add_noinstagram_card: {callback.message.chat.id}')
    await bot.delete_message(chat_id=callback.message.chat.id,
                             message_id=callback.message.message_id)
    await state.set_state(state=None)
    await state.update_data(instagram_card='none')
    data = await state.update_data()
    place_data = {"title": data["title_card"],
                  "short_description": data["short_card"],
                  "long_description": data["long_card"],
                  "address": data["address_card"],
                  "instagram": data["instagram_card"],
                  "yandex_map": data["yandex_card"],
                  "list_image": ','.join(data["image_id_list_image"]),
                  "category": data["category_card"],
                  "sub_category": data["subcategory_card"],
                  "count_link": 0}
    await rq.add_place(data=place_data)

    media = []
    list_image = data["image_id_list_image"]
    for image in list_image:
        media.append(InputMediaPhoto(media=image))
    await callback.message.answer_media_group(media=media)
    await callback.message.answer(text=f'<b>{data["title_card"]}</b>\n'
                                       f'{data["short_card"]}',
                                  reply_markup=keyboard_details(),
                                  parse_mode='html')
    await callback.answer()


@router.message(F.text, StateFilter(Admin.instagram_card))
async def process_get_instagram_card(message: Message, state: FSMContext) -> None:
    """
    Получаем ссылку на инстаграм
    :param message:
    :param state:
    :return:
    """
    logging.info(f'process_get_instagram_card: {message.chat.id}')
    await state.set_state(state=None)
    await state.update_data(instagram_card=message.text)
    data = await state.update_data()
    place_data = {"title": data["title_card"],
                  "short_description": data["short_card"],
                  "long_description": data["long_card"],
                  "address": data["address_card"],
                  "instagram": data["instagram_card"],
                  "yandex_map": data["yandex_card"],
                  "list_image": ','.join(data["image_id_list_image"]),
                  "category": data["category_card"],
                  "sub_category": data["subcategory_card"],
                  "count_link": 0}
    await rq.add_place(data=place_data)

    media = []
    list_image = data["image_id_list_image"]
    for image in list_image:
        media.append(InputMediaPhoto(media=image))
    await message.answer_media_group(media=media)
    await message.answer(text=f'<b>{data["title_card"]}</b>\n'
                              f'{data["short_card"]}',
                         reply_markup=keyboard_details(),
                         parse_mode='html')


@router.callback_query(F.data == 'details')
async def process_details(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Просмотр детальной информации по заведению
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_details: {callback.message.chat.id}')
    data = await state.update_data()

    if data['instagram_card'] != 'none':
        await callback.message.edit_text(text=f'<b>{data["title_card"]}</b>\n'
                                              f'{data["long_card"]}\n'
                                              f'<i>{data["address_card"]}</i>',
                                         reply_markup=keyboard_full_text(data["yandex_card"],
                                                                         data["instagram_card"]),
                                         parse_mode='html')
    else:
        await callback.message.edit_text(text=f'<b>{data["title_card"]}</b>\n'
                                              f'{data["long_card"]}\n'
                                              f'<i>{data["address_card"]}</i>',
                                         reply_markup=keyboard_full_text_1(data["yandex_card"]),
                                         parse_mode='html')
    await callback.answer()
