import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timezone, datetime
from pathlib import Path


from server.src.error_handling.exceptions.userExceptions import UserNotFound
from server.src.repository.user import get_live_user_by_id
from server.src.services.post_service.rate_limit_upload_url import check_upload_rate_limit
from server.src.services.post_service.post_storage import generate_presigned_upload_url, object_exists,generate_presigned_access_url, get_object_size
from server.src.repository.posts import (
create_post_repo, delete_post_repo, get_post_with_media_repo, get_user_posts_repo, create_media_upload_repo,
get_pending_upload_repo, mark_upload_attached_repo, update_post_repo
)
from server.src.error_handling.exceptions.postException import (
    PostNotFound, EmptyPost, InvalidMediaType, MaxMedia,
    InvalidMedia, UploadedMediaNotFound, FileTooLarge,
    UploadRateLimitExceeded, InvalidPostUpdate, PrivateContent
)
from server.src.schemas.post import PaginationCursor, UploadUrlResponse
from server.src.utils.post_visibility import validate_post_visibility, can_view_post
from server.src.utils.enums import MediaType


MAX_MEDIA = 10
ALLOWED_MEDIA_TYPE = {
    MediaType.IMAGE: {".jpg", ".jpeg", ".png"},
    MediaType.VIDEO: {".mp4"},
}
DEFAULT_MEDIA_EXTENSION = {
    MediaType.IMAGE: ".jpg",
    MediaType.VIDEO: ".mp4",
}
MAX_FILE_SIZE = {"image": 10 * 1024 * 1024, "video": 100 * 1024 * 1024} # 10MB, 100MB


UPLOAD_URL_LIMIT = 10 #rate limiters for getting upload url
 # 10 requests per 20 minutes allowed(used in rate limit file)


async def post_creation(user_id:str, data, session: AsyncSession):
    try:
        # empty post
        if not data.caption and not data.media:
            raise EmptyPost()

        # media limit
        if len(data.media) > MAX_MEDIA:
            raise MaxMedia()

        # media type
        for m in data.media:
            if m.media_type not in ALLOWED_MEDIA_TYPE:
                raise InvalidMediaType()

        for media in data.media:
            expected_prefix = f"user/{user_id}/posts/"

            if not media.object_key.startswith(expected_prefix):
                raise InvalidMedia()

            extension = Path(media.object_key).suffix.lower()
            allowed_extensions = ALLOWED_MEDIA_TYPE[
                media.media_type
            ]

            if extension not in allowed_extensions:
                raise InvalidMediaType()

            exists = object_exists(media.object_key)
            if not exists:
                raise UploadedMediaNotFound()

            real_file_size = get_object_size(media.object_key)
            max_allowed_size = MAX_FILE_SIZE[media.media_type]

            if real_file_size > max_allowed_size:
                raise FileTooLarge()

            upload = await get_pending_upload_repo(
                object_key=media.object_key,
                user_id=user_id,
                session=session
            )
            if not upload:
                raise InvalidMedia()

        post = await create_post_repo(data, user_id, session)

        for media in data.media:
            await mark_upload_attached_repo(
                object_key=media.object_key,
                session=session
            )
        await session.commit()

        return {"post_id": str(post.id), "Created": "Success"}

    except Exception:
        await session.rollback()
        raise


async def post_delete(post_id:str, user_id: str, session: AsyncSession):
    deleted = await delete_post_repo(post_id, user_id, session)

    if not deleted:
        raise PostNotFound()

    return {"post": post_id, "succeeded": "Post Deleted"}


async def post_get(post_id, user, session : AsyncSession):
    post, media = await get_post_with_media_repo(post_id, session)

    if not post:
        raise PostNotFound()

    # visibility check
    await validate_post_visibility(post=post, author=post.author, viewer=user,session=session)

    return {
        "id": str(post.id),
        "caption": post.caption,
        "visibility": post.visibility,
        "created_at": post.created_at,
        "media": [
            {
                "url": generate_presigned_access_url(m.object_key),
                "type": m.media_type,
                "order": m.order_index,
            }
            for m in sorted(post.media, key=lambda x: x.order_index)
        ],
    }


async def user_posts(user_id, pagination, user, session: AsyncSession):
    #freeze dataset
    if pagination.snapshot_time is None:
        pagination.snapshot_time = datetime.now(timezone.utc)

    author = await get_live_user_by_id(user_id=user_id, session=session)

    if not author:
        raise UserNotFound()

    posts = await get_user_posts_repo(user_id=user_id, pagination=pagination, session=session)

    allowed = await can_view_post(
        post=None,
        author=author,
        viewer=user,
        session=session
    )

    if not allowed:
        raise PrivateContent()

    next_cursor = None
    if len(posts) == pagination.limit:
        last_post = posts[-1]

        next_cursor = PaginationCursor(
            next_created_at=last_post.created_at,
            next_id=last_post.id,
            snapshot_time=pagination.snapshot_time
        )

    visible_posts = [
        {
            "id": str(post.id),
            "caption": post.caption,
            "visibility": post.visibility,
            "created_at": post.created_at,
            "media": [
                {
                    "url": generate_presigned_access_url(m.object_key),
                    "type": m.media_type,
                    "order": m.order_index,
                }
                for m in post.media
            ]
        }
        for post in posts
    ]

    return {
        "data": visible_posts,
        "next_cursor": next_cursor
    }


async def post_update(post_id, data, user_id, session):
    update_data = {}

    if data.caption is not None:
        update_data["caption"] = data.caption

    if data.visibility is not None:
        update_data["visibility"] = data.visibility

    if not update_data:
        raise InvalidPostUpdate()

    post = await update_post_repo(
        post_id=post_id,
        user_id=user_id,
        update_data=update_data,
        session=session
    )

    if not post:
        raise PostNotFound()

    await session.commit()

    return {
        "success": "updated",
        "data" : {
            "post_id": str(post.id),
            "caption": post.caption,
            "visibility": post.visibility
        }
    }


async def upload_url_generation(data, user_id, session : AsyncSession):
#user requests upload url(for upload permission)(what uploaded->video,image, who uploaded->authorized current user and where uploaded->minio client bucket)
#generate object key='user/{user_id}/posts/{uuid}.jpg/mp4'->stable storage identity to avoid clash between multiple users upload folder(one user cannot upload file to another), uuid is used to avoid file name collision
#generate_presigned_upload_url= a temporary upload ticket for user to upload a file directly to minIO for limited time.(temp storage access)
#then upload_url(temp upload permission) and object_key(permanent storage reference->stored in db) are returned
#this controls-which user can upload which type of file, which exact location(storage), and for what limited time(10 mins)
    if data.media_type not in ALLOWED_MEDIA_TYPE:
        raise InvalidMediaType()

    max_allowed_size = MAX_FILE_SIZE[data.media_type]

    if data.file_size > max_allowed_size:
        raise FileTooLarge()

    current_requests, retry_after = await check_upload_rate_limit(str(user_id))
    if current_requests > UPLOAD_URL_LIMIT:
        raise UploadRateLimitExceeded(retry_after=retry_after)

    extension = DEFAULT_MEDIA_EXTENSION[data.media_type]

    object_key = (
        f"user/{user_id}/posts/{uuid.uuid4()}{extension}"
    )

    upload_url = generate_presigned_upload_url(object_key)

    await create_media_upload_repo(user_id=user_id,object_key=object_key,media_type=data.media_type,session=session)

    return UploadUrlResponse(
        upload_url=upload_url,
        object_key=object_key
    )

