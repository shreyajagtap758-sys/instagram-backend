from server.src.error_handling.base import AppException


class TooManyAttempts(AppException):
    def __init__(self):
        super().__init__(
            error="too_many_attempts",
            message="Too many requests. Account temporarily blocked",
            status_code=429
        )


