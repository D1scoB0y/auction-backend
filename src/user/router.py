from httpx import AsyncClient
from fastapi import Depends, APIRouter, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

import src.database as _db
import src.client as _client
import src.utils as _utils
import src.exception as _exception
import src.user.schemas as _user_schemas
import src.user.service as _user_service
import src.user.models as _user_models
import src.user.exception as _user_exception
import src.user.utils as _user_utils
import src.user.mail_service as _mail_service
import src.user.mobile_service as _mobile_service


router = APIRouter(prefix='/auth')


@router.post(
    '/users',
    response_model=str,
    status_code=status.HTTP_201_CREATED,
    tags=['Authentication'],
)
@_utils.catch_unexpected_errors
async def create_user(
    data: _user_schemas.RegistrationUser,
    session: AsyncSession = Depends(_db.get_session),
):
    try:
        token = await _user_service.create_user(data, session)
    except _user_exception.UserDataConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
            headers={
                'Error-Presentation': e.error_presentation,
                'Access-Control-Expose-Headers': 'Error-Presentation',
            },
        )

    return token


@router.post(
    '/token',
    response_model=str,
    status_code=status.HTTP_200_OK,
    tags=['Authentication'],
)
@_utils.catch_unexpected_errors
async def login_user(
    credentials: _user_schemas.LoginUser,
    session: AsyncSession = Depends(_db.get_session),
):
    try:
        token = await _user_service.get_token(credentials, session)
    except _user_exception.WrongCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
        )

    return token


@router.post(
    '/google',
    response_model=str,
    status_code=status.HTTP_200_OK,
    tags=['Authentication'],
)
@_utils.catch_unexpected_errors
async def login_with_google(
    data: _user_schemas.LoginWithGoogle,
    session: AsyncSession = Depends(_db.get_session),
    client: AsyncClient = Depends(_client.get_client),
):
    try:
        token = await _user_service.manage_google_auth(data.token, session, client)
    except _user_exception.InvalidJwtError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
        )
    except _user_exception.UserDataConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        )

    return token


@router.put(
    '/users',
    status_code=status.HTTP_204_NO_CONTENT,
    tags=['Update user'],
)
@_utils.catch_unexpected_errors
async def update_user(
    user_data: _user_schemas.UpdateUser,
    user: _user_models.User = Depends(_user_utils.get_current_user),
    session: AsyncSession = Depends(_db.get_session),
):
    try:
        await _user_service.update_user(user_data, user, session)
    except _user_exception.UserDataConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
            headers={
                'Error-Presentation': e.error_presentation,
                'Access-Control-Expose-Headers': 'Error-Presentation',
            },
        )


@router.patch(
    '/password',
    status_code=status.HTTP_204_NO_CONTENT,
    tags=['Update user'],
)
@_utils.catch_unexpected_errors
async def change_password(
    data: _user_schemas.ChangePassword,
    user: _user_models.User = Depends(_user_utils.get_current_user),
    session: AsyncSession = Depends(_db.get_session),
):
    try:
        await _user_service.change_password(data, user, session)
    except _user_exception.UserDataConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        )
    except _user_exception.WrongCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
        )


@router.get(
    '/users',
    response_model=_user_schemas.ReadUser,
    status_code=status.HTTP_200_OK,
    tags=['Authentication'],
)
@_utils.catch_unexpected_errors
async def get_user(
    user: _user_models.User = Depends(_user_utils.get_current_user),
):
    return _user_schemas.ReadUser.model_validate(user).model_dump(by_alias=True)


@router.get(
    '/email-verification',
    status_code=status.HTTP_204_NO_CONTENT,
    tags=['Email verification'],
)
@_utils.catch_unexpected_errors
async def request_email_verification(
    user: _user_models.User = Depends(_user_utils.get_current_user),
):
    try:
        _mail_service.send_email_verification_message(user)
    except _exception.TooManyRequestsError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=e.message,
        )
    except _user_exception.UserDataConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        )


@router.get(
    '/validate-email-verification-token',
    status_code=status.HTTP_204_NO_CONTENT,
    tags=['Email verification'],
)
@_utils.catch_unexpected_errors
async def validate_email_verification_token(
    token: str,
    session: AsyncSession = Depends(_db.get_session),
):
    try:
        await _mail_service.validate_email_verification_token(token, session)
    except _user_exception.InvalidJwtError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )


@router.get(
    '/verification-call',
    status_code=status.HTTP_204_NO_CONTENT,
    tags=['Phone number verification'],
)
@_utils.catch_unexpected_errors
async def request_verification_call(
    user: _user_models.User = Depends(_user_utils.get_current_user),
    session: AsyncSession = Depends(_db.get_session),
    client: AsyncClient = Depends(_client.get_client),
):
    try:
        await _mobile_service.request_verification_call(user, session, client)
    except _user_exception.UserDataConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        )
    except _exception.TooManyRequestsError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=e.message,
        )


@router.get(
    '/validate-phone-verification-code',
    status_code=status.HTTP_204_NO_CONTENT,
    tags=['Phone number verification'],
)
@_utils.catch_unexpected_errors
async def validate_verification_code(
    code: int,
    user: _user_models.User = Depends(_user_utils.get_current_user),
    session: AsyncSession = Depends(_db.get_session),
):
    try:
        await _mobile_service.validate_verification_code(code, user, session)
    except _user_exception.UserDataConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        )
    except _user_exception.InvalidCodeError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        )


@router.get(
    '/reset-password',
    status_code=status.HTTP_204_NO_CONTENT,
    tags=['Password reset'],
)
@_utils.catch_unexpected_errors
async def request_password_reset(
    email: str,
    session: AsyncSession = Depends(_db.get_session),
):
    try:
        await _mail_service.send_password_reset_message(
            email,
            session,
        )
    except _exception.TooManyRequestsError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=e.message,
        )
    except _user_exception.UserNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


@router.patch(
    '/reset-password',
    status_code=status.HTTP_204_NO_CONTENT,
    tags=['Password reset'],
)
@_utils.catch_unexpected_errors
async def reset_password(
    reset_password_data: _user_schemas.ResetPassword,
    session: AsyncSession = Depends(_db.get_session),
):
    try:
        await _mail_service.reset_password(reset_password_data, session)
    except _user_exception.InvalidJwtError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
