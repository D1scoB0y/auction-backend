import time
from email.message import EmailMessage

from sqlalchemy.ext.asyncio import AsyncSession

from src.config import config
import src.user.tasks as _user_tasks
import src.user.models as _user_models
import src.user.exception as _user_exception
import src.user.security as _user_security
import src.user.user_getters as _user_getters
import src.user.schemas as _user_schemas


def _build_message(
    subject: str,
    body: str,
    recipient: str,
) -> EmailMessage:
    message = EmailMessage()
    message['Subject'] = subject
    message['From'] = config.MAIL_SENDER
    message['To'] = recipient
    message.set_content(body)
    return message


def _build_email_verification_message(
    username: str,
    recipient: str,
    token: str,
) -> EmailMessage:
    subject = 'Подтвердите почту для FotoJäger`s Auctions'
    body = f'''\
    Здравствуйте, {username}!
    Перейдите по ссылке для подтверджения адреса электронной почты:
    {config.CLIENT_APP_URL}/email-verification?token={token}\
    '''

    return _build_message(subject, body, recipient)


def _build_reset_password_message(
    username: str,
    recipient: str,
    token: str,
) -> EmailMessage:
    subject = 'Сброс пароля для FotoJäger`s Auctions'
    body = f'''\
    Здравствуйте, {username}! Вы запросили сброс пароля указав эту почту.
    Пройдите по ссылке и действуйте по инструкции:
    {config.CLIENT_APP_URL}/reset-password-step-2?token={token}
    Если вы не запрашивали сброс пароля проигнорируйте это сообщение.\
    '''
    return _build_message(subject, body, recipient)


def send_email_verification_message(
    user: _user_models.User,
) -> None:
    if user.email_is_verified:
        raise _user_exception.UserDataConflictError('User email is already verified')

    token = _user_security.generate_jwt({'email': user.email})
    message = _build_email_verification_message(user.username, user.email, token)

    _user_tasks.send_mail_message.delay(user.email, message.as_string())


async def validate_email_verification_token(
    token: str,
    session: AsyncSession,
) -> None:
    payload = _user_security.parse_jwt(token)
    email = payload.get('email')

    if email is None:
        raise _user_exception.InvalidJwtError('Email verification token is invalid')

    user = await _user_getters.get_user_by_email(email, session)

    if user is None:
        raise _user_exception.InvalidJwtError('Email verification token is invalid. User not found')

    user.email_is_verified = True
    await session.commit()


async def send_password_reset_message(
    email: str,
    session: AsyncSession,
) -> None:
    user = await _user_getters.get_user_by_email(email, session)

    if user is None:
        raise _user_exception.UserNotFound('User with this email does not exist')

    token = _user_security.generate_jwt({
        'email': user.email,
        'exp': time.time() + 60 * 10,
    })

    message = _build_reset_password_message(user.username, user.email, token)
    _user_tasks.send_mail_message.delay(user.email, message.as_string())


async def reset_password(
    reset_password_data: _user_schemas.ResetPassword,
    session: AsyncSession,
) -> None:
    payload = _user_security.parse_jwt(reset_password_data.token)

    try:
        if payload['exp'] <= time.time():
            raise _user_exception.InvalidJwtError('JWT was expired.')

        user = await _user_getters.get_user_by_email(payload['email'], session)
    except KeyError:
        raise _user_exception.InvalidJwtError(
            'Unable to parse payload["email"] or payload["exp"].',
        )

    if user is None:
        raise _user_exception.InvalidJwtError('Invalid reset password token. User not found.')

    user.password = _user_security.hash_password(reset_password_data.new_password)

    await session.commit()
