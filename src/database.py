from typing import AsyncGenerator

from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.config import config


Base = declarative_base()
async_engine = create_async_engine(config.DB_URL)
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
