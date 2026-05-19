import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timezone, datetime
from pathlib import Path


from server.src.services.post_service.post_storage import generate_presigned_upload_url, object_exists,generate_presigned_access_url, get_object_size
from server.src.repository.posts import (
create_post_repo, delete_post_repo, get_post_with_media_repo, get_user_posts_repo, create_media_upload_repo,
get_pending_upload_repo, mark_upload_attached_repo, get_post_for_update_repo
)
from server.src.error_handling.exceptions.postException import (
PostNotFound,EmptyPost,InvalidMediaType,MaxMedia,
InvalidMedia, UploadedMediaNotFound, FileTooLarge
)
from server.src.schemas.post import PaginationCursor, UploadUrlResponse
from server.src.services.post_service.visibility import validate_post_visibility
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
    validate_post_visibility(post, user)

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
            for m in media
        ],
    }


async def user_posts(user_id, pagination, user, session: AsyncSession):
    #freeze dataset
    if pagination.snapshot_time is None:
        pagination.snapshot_time = datetime.now(timezone.utc)

    posts = await get_user_posts_repo(user_id=user_id, pagination=pagination, session=session)

    next_cursor = None
    if len(posts) == pagination.limit:
        last_post = posts[-1]

        next_cursor = PaginationCursor(
            next_created_at=last_post.created_at,
            next_id=last_post.id,
            snapshot_time=pagination.snapshot_time
        )

    return {
        "data": [
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
            if (
                post.visibility == "public"
                or (
                    user
                    and str(post.user_id) == str(user.id)
                )
            )
        ],
        "next_cursor": next_cursor
    }


async def post_update(post_id, data, user_id, session):
    post = await get_post_for_update_repo(user_id, post_id, session)

    if not post:
        raise PostNotFound()

    if data.caption is not None:
        post.caption = data.caption

    if data.visibility is not None:
        post.visibility = data.visibility

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

