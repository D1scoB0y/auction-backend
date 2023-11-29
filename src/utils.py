import logging
from functools import wraps

from fastapi import status, HTTPException


def catch_unexpected_errors(endpoint):
    @wraps(endpoint)
    async def wrapper(*args, **kwargs):
        try:
            res = await endpoint(*args, **kwargs)
        except HTTPException:
            raise
        except Exception as e:
            logging.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return res

    return wrapper
