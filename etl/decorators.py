import logging
import time
from functools import wraps
from typing import Any, Callable

from settings import Settings

settings = Settings()


def backoff(
        start_sleep_time=settings.start_sleep_time,
        factor=settings.factor,
        border_sleep_time=settings.border_sleep_time,
        max_attempts=settings.max_attemts
):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            sleep_time = start_sleep_time
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logging.warning(f"Error: {e}, retrying in "
                                    f"{sleep_time} seconds...")
                    time.sleep(sleep_time)
                    sleep_time = min(sleep_time * factor, border_sleep_time)
                    attempts += 1
            raise Exception(f"Function {func.__name__} failed "
                            f"after {max_attempts} attempts")

        return wrapper

    return decorator
