from database.models import User, Place
from database.models import async_session
from sqlalchemy import select
import logging


"""USER"""


async def add_user(tg_id: int, data: dict) -> None:
    """
    Добавляем нового пользователя если его еще нет в БД
    :param tg_id:
    :param data:
    :return:
    """
    logging.info(f'add_user')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        # если пользователя нет в базе
        if not user:
            session.add(User(**data))
            await session.commit()


async def get_all_users() -> list[User]:
    """
    Получаем список всех пользователей зарегистрированных в боте
    :return:
    """
    logging.info(f'get_all_users')
    async with async_session() as session:
        users = await session.scalars(select(User))
        return users


async def get_list_users() -> list:
    """
    ПОЛЬЗОВАТЕЛЬ - список пользователей верифицированных в боте
    :return:
    """
    logging.info(f'get_list_users')
    async with async_session() as session:
        users = await session.scalars(select(User))
        return [[user.tg_id, user.username] for user in users]


"""PLACES"""


async def add_place(data: dict) -> None:
    """
    Добавляем нового заведения
    :param data:
    :return:
    """
    logging.info(f'add_place')
    async with async_session() as session:
        session.add(Place(**data))
        await session.commit()


async def get_list_category() -> list:
    """
    Получаем список категорий
    :return:
    """
    logging.info(f'get_list_category')
    async with async_session() as session:
        places = await session.scalars(select(Place).order_by(Place.pos_cat))
        set_list = []
        for place in places:
            if place.category not in set_list:
                set_list.append(place.category)
        return set_list


async def get_list_subcategory(category: str) -> list:
    """
    Получаем список подкатегорий
    :return:
    """
    logging.info(f'get_list_subcategory')
    async with async_session() as session:
        places = await session.scalars(select(Place).where(Place.category == category).order_by(Place.pos_sub))
        set_list = []
        for place in places:
            if place.sub_category not in set_list:
                set_list.append(place.sub_category)
        return set_list


async def get_list_card(category: str, sub_category: str) -> list:
    """
    Получаем карточки для категории и подкатегории
    :return:
    """
    logging.info(f'get_list_card {category} / {sub_category}')
    async with async_session() as session:
        places = await session.scalars(select(Place).where(Place.category == category,
                                                           Place.sub_category == sub_category).order_by(Place.position))

        set_list = []
        for place in places:
            set_list.append({"id_place": place.id,
                             "title": place.title,
                             "short_description": place.short_description,
                             "long_description": place.long_description,
                             "address": place.address,
                             "instagram": place.instagram,
                             "yandex_map": place.yandex_map,
                             "list_image": place.list_image})
        return set_list


async def info_card(id_card: int) -> Place:
    """
    Получаем информацию о карточке
    :return:
    """
    logging.info(f'info_card')
    async with async_session() as session:
        return await session.scalar(select(Place).where(Place.id == id_card))


async def set_count_show_card(count: int, id_card: int) -> None:
    """

    :param count:
    :param id_card:
    :return:
    """
    logging.info(f'set_count_show_card')
    async with async_session() as session:
        place = await session.scalar(select(Place).where(Place.id == id_card))
        place.count_link = count
        await session.commit()


async def get_list_card_event() -> list:
    """
    Получаем список карточек мероприятий
    :return:
    """
    logging.info(f'get_list_card_event')
    async with async_session() as session:
        places = await session.scalars(select(Place).where(Place.category == "🎧Мероприятия недели").order_by(Place.position))
        set_list = []
        for place in places:
            set_list.append({"id_place": place.id,
                             "title": place.title,
                             "short_description": place.short_description,
                             "long_description": place.long_description,
                             "address": place.address,
                             "instagram": place.instagram,
                             "yandex_map": place.yandex_map,
                             "list_image": place.list_image})
        return set_list


async def get_list_card_stat() -> list:
    """
    Получаем список названий мест и количество переходов по ним
    :return:
    """
    logging.info(f'get_list_card_stat')
    async with async_session() as session:
        places = await session.scalars(select(Place))
        return [[place.title, place.count_link] for place in places]


async def delete_card(id_place: int) -> None:
    """
    Удаление карточки заведения
    :return:
    """
    logging.info(f'delete_card')
    async with async_session() as session:
        place = await session.scalar(select(Place).where(Place.id == id_place))
        await session.delete(place)
        await session.commit()


async def set_position_category(category: str) -> None:
    """
    Обновляем позиции категории в выдаче
    :return:
    """
    logging.info(f'set_position_category')
    async with async_session() as session:
        places = await session.scalars(select(Place).order_by(Place.position))
        for place in places:
            if place.category == category:
                place.pos_cat = 0
            else:
                place.pos_cat += 1
        await session.commit()


async def set_position_sub_category(category: str, sub_category: str) -> None:
    """
    Обновляем позицию подкатегории в выдаче категории
    :return:
    """
    logging.info(f'set_position_category')
    async with async_session() as session:
        places = await session.scalars(select(Place).where(Place.category == category).order_by(Place.position))
        for place in places:
            if place.sub_category == sub_category:
                place.pos_sub = 0
            else:
                place.pos_sub += 1
        await session.commit()


async def set_position_card(category: str, sub_category: str, id_card: int) -> None:
    """
    Обновляем позицию карточки заведения
    :return:
    """
    logging.info(f'set_position_category: category-{category} sub_category-{sub_category} id_card-{id_card}')
    async with async_session() as session:
        places = await session.scalars(select(Place).where(Place.category == category,
                                                           Place.sub_category == sub_category).order_by(Place.position))
        for place in places:
            print(place.title)
            if place.id == id_card:
                place.position = 0
            else:
                place.position += 1
        await session.commit()


async def set_attribute_card(attribute: str, set_attribute: str, id_card: int) -> None:
    """
    Обновляем поля карточки заведения
    :return:
    """
    logging.info(f'set_position_category')
    async with async_session() as session:
        place = await session.scalar(select(Place).where(Place.id == id_card))
        if attribute == 'title':
            place.title = set_attribute
        elif attribute == 'category':
            place.category = set_attribute
        elif attribute == 'short_description':
            place.short_description = set_attribute
        elif attribute == 'long_description':
            place.long_description = set_attribute
        elif attribute == 'address':
            place.address = set_attribute
        await session.commit()
