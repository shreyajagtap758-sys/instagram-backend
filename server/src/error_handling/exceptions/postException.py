
from server.src.error_handling.base import AppException


class EmptyPost(AppException):
    def __init__(self):
        super().__init__(
            error="post_empty",
            message="to create a post, you must add caption and media",
            status_code=404
        )

class MaxMedia(AppException):
    def __init__(self):
        super().__init__(
            error="not_allowed",
            message="Maximum 10 media items are allowed per post",
            status_code=405
        )

class InvalidMediaType(AppException):
    def __init__(self):
        super().__init__(
            error="media_type_not_allowed",
            message="media type must be only 'image', 'video'",
            status_code=406
        )

class PostNotFound(AppException):
    def __init__(self):
        super().__init__(
            error="not_found",
            message="post not found",
            status_code=404
        )

class PrivateContent(AppException):
    def __init__(self):
        super().__init__(
            error="private",
            message="content is private",
            status_code=403
        )

class UploadedMediaNotFound(AppException):
    def __init__(self):
        super().__init__(
            error="Not_Found",
            message="uploaded media not found",
            status_code=400
        )

class InvalidMedia(AppException):
    def __init__(self):
        super().__init__(
            error="Invalid",
            message="not allowed to use this media",
            status_code=403
        )

