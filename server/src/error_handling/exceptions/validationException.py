

from server.src.error_handling.base import AppException


class PasswordLengthError(AppException):
    def __init__(self):
        super().__init__(
            error="password_invalid_length",
            message="Password must be 8-30 characters long",
            status_code=400
        )


class PasswordComplexityError(AppException):
    def __init__(self):
        super().__init__(
            error="password_missing_requirements",
            message="Password must contain uppercase, lowercase, number, and special character",
            status_code=400
        )


class PasswordCommonError(AppException):
    def __init__(self):
        super().__init__(
            error="password_too_common",
            message="Password is too common",
            status_code=400
        )


class PasswordSpaceError(AppException):
    def __init__(self):
        super().__init__(
            error="password_contains_spaces",
            message="Password cannot contain spaces",
            status_code=400
        )


class UsernameLengthError(AppException):
    def __init__(self):
        super().__init__(
            error="username_invalid_length",
            message="Username must be 3–30 characters long",
            status_code=400
        )


class UsernameFormatError(AppException):
    def __init__(self):
        super().__init__(
            error="username_invalid_format",
            message="Username can only contain lowercase letters, uppercase letters, numbers, and underscores",
            status_code=400
        )

