import datetime as dt

from starlette.datastructures import UploadFile as StarletteFile

import src.auction.utils as _auction_utils


def validate_images(images: list[StarletteFile]) -> list[StarletteFile]:
    if not len(images):
        raise ValueError('Minimum 1 image')

    if len(images) > 12:
        raise ValueError('Maximum 12 image')

    for img in images:

        if not isinstance(img, StarletteFile):
            raise ValueError('Must be a UploadFile')

        if img.size:

            if img.size > (1024**2) * 8:  # 8 MB
                raise ValueError('Max image size is 8 MB')

    return images


def validate_end_date(end_date: dt.datetime) -> dt.datetime:
    end_date = end_date.replace(tzinfo=None)

    if end_date <= _auction_utils.current_datetime():
        raise ValueError('The auction end date must be later than the auction creation date.')

    if end_date - _auction_utils.current_datetime() > dt.timedelta(days=21):
        raise ValueError('Max auction duration - 21 days')

    return end_date
