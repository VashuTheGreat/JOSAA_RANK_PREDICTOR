from functools import wraps
import logging
import sys
from exception import MyException


def asyncHandler(func):
    wraps(func)

    async def wrapper(*args,**kwargs):
        try:
            return await func(*args,**kwargs)
        except Exception as e:
            err=MyException(e,sys)
            logging.error(err)
            raise err
    return wrapper    