
from server.src.error_handling.base import AppException


class EmailAlreadyExists(AppException):
    def __init__(self):
        super().__init__(
            error="email_already_exists",
            message="Email already exists",
            status_code=400
        )


class UserNotFound(AppException):
    def __init__(self):
        super().__init__(
            error="user_not_found",
            message="User not found",
            status_code=404
        )

