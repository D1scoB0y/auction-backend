import base64

from src.exception import AppException


class UserDataConflictError(AppException):
    def __init__(self, message: str, error_presentation: str = ''):
        super().__init__(message)
        self.error_presentation = base64.b64encode(
            error_presentation.encode(),
        ).decode()


class UserNotFound(AppException):
    pass


class InvalidJwtError(AppException):
    pass


class WrongCredentialsError(AppException):
    pass


class PhoneCallFailedError(AppException):
    pass


class InvalidCodeError(AppException):
    pass
