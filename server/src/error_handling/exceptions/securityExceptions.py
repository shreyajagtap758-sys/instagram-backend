from server.src.error_handling.base import AppException


class TooManyAttempts(AppException):
    def __init__(self):
        super().__init__(
            error="too_many_attempts",
            message="Too many requests. try again later",
            status_code=429
        )

class SamePass(AppException):
    def __init__(self):
        super().__init__(
            error="same_as_old_password",
            message="please provide another password",
            status_code=400
        )


