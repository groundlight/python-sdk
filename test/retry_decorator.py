"""Test-only helpers for retrying tests affected by transient cloud timing."""

import functools
import time
from typing import Any, Callable, Tuple, Type


def retry_on_failure(
    *,
    max_attempts: int = 2,
    exception_types: Tuple[Type[BaseException], ...] = (AssertionError,),
    retry_delay_seconds: float = 5.0,
) -> Callable[[Callable[..., Any]], Callable[..., None]]:
    """Run the wrapped test up to `max_attempts` times when it raises a listed exception."""

    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    def decorator(fn: Callable[..., Any]) -> Callable[..., None]:
        @functools.wraps(fn)
        def wrapper(*args: object, **kwargs: object) -> None:
            for attempt in range(max_attempts):
                try:
                    fn(*args, **kwargs)
                    return
                except exception_types:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(retry_delay_seconds)

        return wrapper

    return decorator
