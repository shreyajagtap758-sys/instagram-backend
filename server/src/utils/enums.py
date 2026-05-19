from enum import Enum

class Visibility(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"


class MediaType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"


class PostStatus(str, Enum):
    PUBLISHED = "published"
    DELETED = "deleted"


class UploadStatus(str, Enum):
    PENDING = "pending"
    ATTACHED = "attached"