import random
from typing import Any

import jwt
import bcrypt

from src.config import config
import src.user.exception as _user_exception


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def check_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password.encode())


def generate_jwt(payload: dict) -> str:
    return jwt.encode(payload, config.SECRET_KEY, algorithm='HS256')


def parse_jwt(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=['HS256'])
    except jwt.exceptions.InvalidTokenError:
        raise _user_exception.InvalidJwtError('JWT is unparsable')

    return payload


def generate_4_digit_code() -> int:
    return random.randrange(1_000, 10_000)
