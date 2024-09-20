from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


from config_data.config import Config, load_config
from keyboards.admin_main_keyboards import keyboards_start_admin
from filter.admin_filter import IsSuperAdmin
from database import requests as rq

import logging

router = Router()

config: Config = load_config()


class User(StatesGroup):
    article = State()


@router.message(CommandStart(), IsSuperAdmin())
async def process_start_command_user(message: Message, state: FSMContext) -> None:
    """
    Бот запущен администратором
    :param message:
    :param state:
    :return:
    """
    logging.info(f'process_start_command_user: {message.chat.id}')
    await state.update_data(user_name=message.from_user.username)
    await message.answer(text=f'Здравствуй, {message.from_user.first_name}!'
                              f'Вы являетесь супер админом проекта и вам доступен расширенный функционал для'
                              f' правки контента',
                         reply_markup=keyboards_start_admin())


@router.message(F.text == '📋 Статистика', IsSuperAdmin())
async def process_get_stat(message: Message) -> None:
    """
    Получаем статистику по переходам по карточкам и пользователям
    :param message:
    :return:
    """
    logging.info(f'process_get_stat: {message.chat.id}')
    stat = await rq.get_list_card_stat()
    text = 'Статистика:\n'
    i = 0
    count_row = 100
    for card in stat:
        i += 1
        text += f'<b>{card[0]}:</b> {card[1]}\n'
        if i % count_row == 0:
            await message.answer(text=f'{text}',
                                 parse_mode='html')
            text = ''
    if i % count_row:
        await message.answer(text=f'{text}',
                             parse_mode='html')
    list_id_username = await rq.get_list_users()
    await message.answer(text=f'Количество уникальных пользователей: {len(list_id_username)}')
