from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import config
import src.user.models as _user_models
import src.user.security as _user_security
import src.user.exception as _user_exception


async def call(
    phone_number: str,
    verif_code: int,
    client: AsyncClient,
):
    call_data = {
        'phone': phone_number,
        'phone_suffix': str(verif_code),
        'public_key': config.PHONE_SERVICE_API_KEY,
        'campaign_id': config.PHONE_SERVICE_COMPAIGN_ID,
    }

    response = await client.post(
        'https://zvonok.com/manager/cabapi_external/api/v1/phones/flashcall/',
        data=call_data,
    )

    if response.json()['status'] != 'ok':
        raise _user_exception.PhoneCallFailedError('Phone call was failed.')


async def request_verification_call(
    user: _user_models.User,
    session: AsyncSession,
    client: AsyncClient,
) -> None:
    if user.phone_number is None:
        raise _user_exception.UserDataConflictError('User has not set a phone number')

    verif_code = _user_security.generate_4_digit_code()

    await call(user.phone_number, verif_code, client)

    user.phone_number_verif_code = verif_code
    await session.commit()


async def validate_verification_code(
    verif_code: int,
    user: _user_models.User,
    session: AsyncSession,
) -> None:
    if user.phone_number is None:
        raise _user_exception.UserDataConflictError(
            'User dont have phone number. Unable to confirm it.',
        )

    if verif_code != user.phone_number_verif_code:
        raise _user_exception.InvalidCodeError('Phone number verification code is invalid.')

    user.phone_number_is_verified = True
    user.phone_number_verif_code = None

    await session.commit()
