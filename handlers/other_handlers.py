from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.types import FSInputFile
import asyncio
from database import requests as rq
from services.get_exel import list_users_to_exel
import logging

router = Router()


@router.callback_query()
async def all_calback(callback: CallbackQuery) -> None:
    logging.info(f'all_calback: {callback.message.chat.id}')
    logging.info(callback.data)


@router.message()
async def all_message(message: Message) -> None:
    logging.info(f'all_message')
    if message.photo:
        logging.info(f'all_message message.photo')
        logging.info(message.photo[-1].file_id)

    if message.sticker:
        logging.info(f'all_message message.sticker')
        # Получим ID Стикера
        # print(message.sticker.file_id)

    if message.text == '/get_logfile':
        file_path = "py_log.log"
        await message.answer_document(FSInputFile(file_path))

    if message.text == '/get_dbfile':
        file_path = "database/db.sqlite3"
        await message.answer_document(FSInputFile(file_path))

    if message.text == '/get_listusers':
        logging.info(f'all_message message.admin./get_listusers')
        list_user = await rq.get_all_users()
        text = 'Список пользователей:\n'
        for i, user in enumerate(list_user):
            text += f'{i + 1}. @{user.username}/{user.tg_id}\n\n'
            if i % 10 == 0 and i > 0:
                await asyncio.sleep(0.2)
                await message.answer(text=text)
                text = ''
        await message.answer(text=text)

    if message.text == '/get_exelusers':
        logging.info(f'all_message message.admin./get_exelusers')
        await list_users_to_exel()
        file_path = "list_user.xlsx"
        await message.answer_document(FSInputFile(file_path))

    else:
        await message.answer('Я вас не понимаю!')
