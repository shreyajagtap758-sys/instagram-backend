from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timezone, datetime


from server.src.repository.posts import create_post_repo, delete_post_repo, get_post_with_media_repo, get_user_posts_repo
from server.src.error_handling.exceptions.postException import (
PostNotFound,PrivateContent,EmptyPost,InvalidMediaType,MaxMedia
)
from server.src.schemas.post import PaginationCursor


MAX_MEDIA = 10


async def post_creation(user_id:str, data, session: AsyncSession):
    #empty post
    if not data.caption and not data.media:
        raise EmptyPost()

    #media limit
    if len(data.media) > MAX_MEDIA:
        raise MaxMedia()

    #media type
    for m in data.media:
        if m.media_type not in {"image", "video"}:
            raise InvalidMediaType()

    post = await create_post_repo(data, user_id, session)

    return {"post_id": str(post.id)}


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
    if post.visibility == "private":
        if not user or str(post.user_id) != str(user.id):
            raise PrivateContent()

    return {
        "id": str(post.id),
        "caption": post.caption,
        "visibility": post.visibility,
        "created_at": post.created_at,
        "media": [
            {
                "url": m.media_url,
                "type": m.media_type,
                "order": m.order_index,
            }
            for m in media
        ],
    }


async def user_posts(user_id, pagination, session: AsyncSession):
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
            }
            for post in posts
        ],
        "next_cursor": next_cursor
    }
