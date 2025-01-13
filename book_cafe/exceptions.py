from functools import wraps
from typing import Callable

from redis.exceptions import RedisError
from sqlalchemy.exc import SQLAlchemyError

from book_cafe.app_logger import logger


def sql_alchemy_exception() -> Callable:
    def decorator(f: Callable):
        @wraps(f)
        def wrapped(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except SQLAlchemyError:
                logger.error("SQLAlchemyError")
        return wrapped
    return decorator


def reddis_exception() -> Callable:
    def decorator(f: Callable):
        @wraps(f)
        def wrapped(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except RedisError:
                logger.error("RedisError")
        return wrapped
    return decorator


if __name__ == "__main__":
    pass