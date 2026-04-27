# all custom errors
from server.src.error_handling.base import AppException

class UnauthorizedError(AppException):
    def __init__(self):
        super().__init__(
            error="unauthorized",
            message="Unauthorized",
            status_code=401
        )


class InvalidCredentials(AppException):
    def __init__(self):
        super().__init__(
            error="invalid_credentials",
            message="Invalid credentials, please retry",
            status_code=401
        )


class InvalidToken(AppException):
    def __init__(self):
        super().__init__(
            error="invalid_token",
            message="Unauthorized",
            status_code=401
        )


class InvalidRefreshToken(AppException):
    def __init__(self):
        super().__init__(
            error="invalid_refresh_token",
            message="Unauthorized",
            status_code=401
        )

class TokenExpired(AppException):
    def __init__(self):
        super().__init__(
            error="invalid/expired_token",
            message="provide new",
            status_code=401
        )

