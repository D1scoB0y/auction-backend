from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

import src.database as _db
import src.user.security as _user_security
import src.user.user_getters as _user_getters
import src.user.exception as _user_exception


oauth2schema = OAuth2PasswordBearer(tokenUrl='/auth/token')


async def get_current_user(
    token: str = Depends(oauth2schema),
    session: AsyncSession = Depends(_db.get_session),
):
    try:
        payload = _user_security.parse_jwt(token)

        try:
            user_id = int(payload['id'])
        except KeyError:
            raise _user_exception.InvalidJwtError('Oauth token is invalid.')

        user = await _user_getters.get_user_by_id(user_id, session)

        if user is None:
            raise _user_exception.UserNotFound('Oauth token is invalid. Service cant find you.')

        return user
    except _user_exception.InvalidJwtError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
        )
    except _user_exception.UserNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
        )
