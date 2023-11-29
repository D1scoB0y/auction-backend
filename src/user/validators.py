import re


def validate_username(username: str) -> str:
    if not isinstance(username, str):
        raise ValueError('Username should be a string')

    if not (3 <= len(username) <= 20):
        raise ValueError('Username length should be from 3 to 30')

    special_sybmols = '!@#$%^&*()-=+{][;:"\'\\<>,.?/`~|}'

    for symbol in special_sybmols:
        if symbol in username:
            raise ValueError('Username must not contain special symbols')

    return username


def validate_email(email: str) -> str:
    if not isinstance(email, str):
        raise ValueError('Email should be a string')

    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

    if not re.fullmatch(regex, email):
        raise ValueError('Email is invalid')

    return email


def validate_phone(phone: str | None):
    if phone is None:
        return None

    if not isinstance(phone, str):
        raise ValueError('Phone number should be a string or None')

    if phone[0] != '+':
        raise ValueError('Phone number should starts with "+"')

    if (len(phone)) < 12:
        raise ValueError('Phone length should equal 12')

    return phone


def validate_password(password: str) -> str:
    if not isinstance(password, str):
        raise ValueError('Password should be a string')

    if not (8 <= len(password) <= 64):
        raise ValueError('Password length - from 8 to 64')

    return password
