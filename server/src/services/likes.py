from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


from server.src.repository.user import get_live_user_by_id
from server.src.schemas.like import LikeCursorPagination
from server.src.repository.posts import (get_post_by_id_repo)
from server.src.repository.like import (
    like_post_repo,
    unlike_post_repo, get_user_liked_posts_repo, get_post_likes_repo
)
from server.src.error_handling.exceptions.postException import PostNotFound
from server.src.utils.enums import PostStatus
from server.src.utils.post_visibility import validate_post_visibility


async def like_a_post(
    post_id,
    user,
    session: AsyncSession
):

    async with session.begin():

        # Validate post INSIDE transaction.
        # Prevents race windows where post is deleted
        # after validation but before like insert.
        post = await get_post_by_id_repo(
            post_id=post_id,
            session=session
        )

        if not post or post.status == PostStatus.DELETED:
            raise PostNotFound()

        author = await get_live_user_by_id(user_id=post.author_id, session=session)
        if not author:
            raise PostNotFound()

        await validate_post_visibility(post=post, author=author, viewer=user, session=session)

        # Repo handles:
        # - insert
        # - idempotency
        # - atomic counter increment
        # - returning updated count
        result = await like_post_repo(
            post_id=post_id,
            user_id=user.id,
            session=session
        )

    return {
        "liked": True,
        "like_count": result["like_count"],
        "new_like_created": result["inserted"]
    }


async def unlike_a_post(
    post_id,
    user,
    session: AsyncSession
):

    async with session.begin():

        # Validate inside transaction.
        post = await get_post_by_id_repo(
            post_id=post_id,
            session=session
        )

        if not post or post.status == PostStatus.DELETED:
            raise PostNotFound()

        author = await get_live_user_by_id(user_id=post.author_id, session=session)
        if not author:
            raise PostNotFound()

        await validate_post_visibility(post=post, author=author, viewer=user, session=session)

        # Repo handles:
        # - delete
        # - idempotency
        # - atomic decrement
        # - returning updated count
        result = await unlike_post_repo(
            post_id=post_id,
            user_id=user.id,
            session=session
        )

    return {
        "liked": False,
        "like_count": result["like_count"],
        "like_removed": result["deleted"]
    }

# get users who liked a post
async def get_liked_post_users(
    post_id,
    user,
    pagination: LikeCursorPagination,
    session: AsyncSession
):

    post = await get_post_by_id_repo(
        post_id=post_id,
        session=session
    )

    if not post or post.status == PostStatus.DELETED:
        raise PostNotFound()

    author = await get_live_user_by_id(user_id=post.author_id, session=session)
    await validate_post_visibility(post=post, author=author, viewer=user, session=session)

    result = await get_post_likes_repo(
        post_id=post_id,
        pagination=pagination,
        session=session
    )

    return result

#get posts liked by a user, only owner can see it
async def get_liked_user_posts(
    requested_user_id,
    current_user,
    pagination: LikeCursorPagination,
    session: AsyncSession
):

    if requested_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    result = await get_user_liked_posts_repo(
        user_id=requested_user_id,
        pagination=pagination,
        session=session
    )

    return result


