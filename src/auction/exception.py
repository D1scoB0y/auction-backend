from src.exception import AppException


class MissingPermissionsError(AppException):
    pass


class LotNotFoundError(AppException):
    pass


class InactiveLotError(AppException):
    pass


class BidValueError(AppException):
    pass
