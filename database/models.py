from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine


engine = create_async_engine(url="sqlite+aiosqlite:///database/db.sqlite3", echo=False)
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(Integer)
    username: Mapped[str] = mapped_column(String(20))


class Place(Base):
    __tablename__ = 'places'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(20))
    short_description: Mapped[str] = mapped_column(String(20))
    long_description: Mapped[str] = mapped_column(String(20))
    address: Mapped[str] = mapped_column(String(20))
    instagram: Mapped[str] = mapped_column(String(20))
    yandex_map: Mapped[str] = mapped_column(String(20))
    list_image: Mapped[str] = mapped_column(String(20))
    category: Mapped[str] = mapped_column(String(20))
    sub_category: Mapped[str] = mapped_column(String(20))
    count_link: Mapped[int] = mapped_column(Integer)
    position: Mapped[int] = mapped_column(Integer, default=0)
    pos_cat: Mapped[int] = mapped_column(Integer, default=0)
    pos_sub: Mapped[int] = mapped_column(Integer, default=0)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

