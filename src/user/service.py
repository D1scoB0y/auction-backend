import random

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import config
import src.user.models as _user_models
import src.user.schemas as _user_schemas
import src.user.security as _user_security
import src.user.user_getters as _user_getters
import src.user.exception as _user_exception
import src.user.google_service as _google_service


async def get_token(
    credentials: _user_schemas.LoginUser,
    session: AsyncSession,
) -> str:
    user = await _user_getters.get_user_by_email(credentials.email, session)

    if user is None:
        raise _user_exception.WrongCredentialsError('Wrong credentials.')

    if user.password is None:
        raise _user_exception.WrongCredentialsError('Credentials authentication is unavailable')

    is_passwords_match = _user_security.check_password(credentials.password, user.password)

    if not is_passwords_match:
        raise _user_exception.WrongCredentialsError('Wrong credentials.')

    return _user_security.generate_jwt({'id': user.user_id})


async def create_user(
    data: _user_schemas.RegistrationUser,
    session: AsyncSession,
) -> str:
    user_with_same_username = await _user_getters.get_user_by_username(data.username, session)

    if user_with_same_username is not None:
        raise _user_exception.UserDataConflictError(
            'Username is already taken.',
            'Это имя уже занято',
        )

    user_with_same_email = await _user_getters.get_user_by_email(data.email, session)

    if user_with_same_email is not None:
        raise _user_exception.UserDataConflictError(
            'Email is already taken.',
            'Эта почта уже занята',
        )

    new_user = _user_models.User(**data.model_dump(by_alias=True))
    new_user.password = _user_security.hash_password(data.password)
    session.add(new_user)

    await session.commit()
    await session.refresh(new_user)

    return _user_security.generate_jwt({'id': new_user.user_id})


async def update_user(
    user_data: _user_schemas.UpdateUser,
    user: _user_models.User,
    session: AsyncSession,
) -> None:
    if user_data.username != user.username:
        user_with_same_username = await _user_getters.get_user_by_username(
            user_data.username,
            session,
        )

        if user_with_same_username is not None:
            raise _user_exception.UserDataConflictError(
                'Username is already taken.',
                'Имя пользователя уже занято',
            )

        user.username = user_data.username

    if user_data.email != user.email:
        user_with_same_email = await _user_getters.get_user_by_email(user_data.email, session)

        if user_with_same_email is not None:
            raise _user_exception.UserDataConflictError(
                'Email is already taken.',
                'Электронная почта уже занята',
            )

        user.email_is_verified = False
        user.email = user_data.email

    if user_data.phone_number is None:
        user.phone_number_is_verified = False
    else:
        if user_data.phone_number != user.phone_number:
            user_with_same_phone_number = await _user_getters.get_user_by_phone_number(
                user_data.phone_number,
                session,
            )

            if user_with_same_phone_number is not None:
                raise _user_exception.UserDataConflictError(
                    'Phone number is already taken.',
                    'Номер телефона уже занят',
                )

            user.phone_number_is_verified = False
            user.phone_number = user_data.phone_number

    user.contacts = user_data.contacts
    await session.commit()


async def manage_google_auth(
    google_access_token: str,
    session: AsyncSession,
    client: AsyncClient,
) -> str:
    google_user_data = await _google_service.get_user_data_from_google(google_access_token, client)
    email = google_user_data.get('email')
    user = await _user_getters.get_user_by_email(email, session)

    if user is not None:
        return _user_security.generate_jwt({'id': user.user_id})

    username = google_user_data.get('given_name')

    while True:
        user_with_same_username = await _user_getters.get_user_by_username(username, session)

        if user_with_same_username is None:
            break

        if len(username) == 16:
            raise _user_exception.UserDataConflictError('Username is already taken.')

        username += str(random.randint(1, 9))

    new_user = _user_models.User(
        username=username,
        email=email,
        created_via_google=True,
    )
    session.add(new_user)

    await session.commit()
    await session.refresh(new_user)

    return _user_security.generate_jwt({'id': new_user.user_id})


async def change_password(
    data: _user_schemas.ChangePassword,
    user: _user_models.User,
    session: AsyncSession,
) -> None:
    if user.password is None:
        raise _user_exception.UserDataConflictError('User have no password')

    if not _user_security.check_password(data.current_password, user.password):
        raise _user_exception.WrongCredentialsError('Password is invalid.')

    user.password = _user_security.hash_password(data.new_password)
    await session.commit()
