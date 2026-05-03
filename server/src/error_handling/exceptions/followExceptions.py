
from server.src.error_handling.base import AppException


class InvalidRequest(AppException):
    def __init__(self):
        super().__init__(
            error="Invalid_Operation",
            message="Already following or invalid request",
            status_code=429
        )

class NoRelationFound(AppException):
    def __init__(self):
        super().__init__(
            error="Invalid_Operation",
            message="Follow relationship not found",
            status_code=429
        )

class SelfFollow(AppException):
    def __init__(self):
        super().__init__(
            error="SELF_FOLLOW",
            message="Can not follow yourself",
            status_code=429
        )

class AlreadyFollowing(AppException):
    def __init__(self):
        super().__init__(
            error="followed",
            message="you have followed this user",
            status_code=429
        )


class SelfUnfollow(AppException):
    def __init__(self):
        super().__init__(
            error="self-operation",
            message="can not unfollow yourself",
            status_code=429
        )
