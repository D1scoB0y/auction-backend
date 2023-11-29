from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

import src.user.models as _user_models


async def get_user_by_id(
    user_id: int,
    session: AsyncSession,
) -> _user_models.User | None:
    return await session.get(_user_models.User, user_id)


async def get_user_by_email(
    email: str,
    session: AsyncSession,
) -> _user_models.User | None:
    res = await session.execute(
        select(_user_models.User).where(_user_models.User.email == email)
    )
    return res.scalar()


async def get_user_by_username(
    username: str,
    session: AsyncSession,
) -> _user_models.User | None:
    res = await session.execute(
        select(_user_models.User).where(_user_models.User.username == username)
    )
    return res.scalar()


async def get_user_by_phone_number(
    phone_number: str,
    session: AsyncSession,
) -> _user_models.User | None:
    res = await session.execute(
        select(_user_models.User).where(_user_models.User.phone_number == phone_number)
    )
    return res.scalar()
