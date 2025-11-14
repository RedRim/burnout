from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import Field, Session, SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config import setup_config

DATABASE_URL = setup_config().db.dsn
SYNC_DATABASE_URL = setup_config().db.sync_dsn
engine = create_async_engine(DATABASE_URL)
sync_engine = create_engine(SYNC_DATABASE_URL)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
session_maker = sessionmaker(sync_engine, class_=Session, expire_on_commit=False)


class Base(SQLModel):
    """
    Базовая модель
    """

    id: int | None = Field(default=None, primary_key=True)


class RoleUserModel(Base):
    """
    Поля пользователя создавшего модель
    """

    created_by_id: int | None = None


class TimestampedModel(Base):
    """
    Поля пользователя создавшего модель
    """

    created_datetime: datetime | None = Field(  # type: ignore
        default=None,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"server_default": func.now()},
    )
    updated_datetime: datetime | None = Field(  # type: ignore
        default=None,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"onupdate": datetime.now, "server_default": func.now()},
    )


class DomainModel(RoleUserModel, TimestampedModel):
    """
    Общие поля для объектов доменной модели
    """
