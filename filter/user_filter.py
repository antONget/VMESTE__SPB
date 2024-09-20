from module.data_base import get_list_users
import logging


def check_user(telegram_id: int) -> bool:
    logging.info('check_user')
    list_user = get_list_users()
    for info_user in list_user:
        if info_user[0] == telegram_id:
            return True
    return False