from httpx import AsyncClient

from src.config import config
import src.user.exception as _user_exception


async def get_user_data_from_google(access_token: str, client: AsyncClient):
    res = await client.get(
        f'https://www.googleapis.com/oauth2/v1/userinfo?access_token={access_token}',
        headers={
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
        },
    )
    user_data = res.json()

    try:
        user_data['id']
    except KeyError:
        raise _user_exception.InvalidJwtError(
            'Google access token is invalid. We cant get user data from google.',
        )

    return user_data


async def get_recaptcha_score(token: str, client: AsyncClient) -> float:
    if not token:
        return 1.0

    api = f'https://www.google.com/recaptcha/api/siteverify \
        ?secret={config.GOOGLE_RECAPTCHA_SECRET_KEY}&response={token}'
    res = await client.post(api)
    res = res.json()

    if res['success']:
        return res['score']

    return 1.0
