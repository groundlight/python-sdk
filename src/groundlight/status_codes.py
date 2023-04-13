# Helper functions for checking HTTP status codes.

OK_MIN = 200
OK_MAX = 299
USER_ERROR_MIN = 400
USER_ERROR_MAX = 499


def is_ok(status_code: int) -> bool:
    return OK_MIN <= status_code <= OK_MAX


def is_user_error(status_code: int) -> bool:
    return USER_ERROR_MIN <= status_code <= USER_ERROR_MAX
