# Helper functions for checking HTTP status codes.


# We can use range because of Python's lazy evaluation. Thus, the values
# in the range are actually not generated, so we still get O(1) time complexity
OK_RANGE = range(200, 300)
USER_ERROR_RANGE = range(400, 500)


def is_ok(status_code: int) -> bool:
    return status_code in OK_RANGE


def is_user_error(status_code: int) -> bool:
    return status_code in USER_ERROR_RANGE
