from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from server.src.schemas.like import LikeCursorPagination
from server.src import models
from server.src.repository.posts import (get_post_by_id_repo)
from server.src.repository.like import (
    like_post_repo,
    unlike_post_repo, get_user_liked_posts_repo, get_post_likes_repo
)
from server.src.error_handling.exceptions.postException import PostNotFound
from server.src.utils.enums import PostStatus


async def like_a_post(
    post_id,
    user_id,
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

        if not post:
            raise PostNotFound()

        if post.status == PostStatus.DELETED:
            raise PostNotFound()

        # Repo handles:
        # - insert
        # - idempotency
        # - atomic counter increment
        # - returning updated count
        result = await like_post_repo(
            post_id=post_id,
            user_id=user_id,
            session=session
        )

    return {
        "liked": True,
        "like_count": result["like_count"],
        "new_like_created": result["inserted"]
    }


# =========================================================
# UNLIKE POST
# =========================================================

async def unlike_a_post(
    post_id,
    user_id,
    session: AsyncSession
):

    async with session.begin():

        # Validate inside transaction.
        post = await get_post_by_id_repo(
            post_id=post_id,
            session=session
        )

        if not post:
            raise PostNotFound()

        if post.status == PostStatus.DELETED:
            raise PostNotFound()

        # Repo handles:
        # - delete
        # - idempotency
        # - atomic decrement
        # - returning updated count
        result = await unlike_post_repo(
            post_id=post_id,
            user_id=user_id,
            session=session
        )

    return {
        "liked": False,
        "like_count": result["like_count"],
        "like_removed": result["deleted"]
    }


# =========================================================
# GET USERS WHO LIKED A POST
# =========================================================

async def get_liked_post_users(
    post_id,
    pagination: LikeCursorPagination,
    session: AsyncSession
):

    # Read-only endpoint.
    # No transaction needed.

    post = await get_post_by_id_repo(
        post_id=post_id,
        session=session
    )

    if not post:
        raise PostNotFound()

    if post.status == PostStatus.DELETED:
        raise PostNotFound()

    result = await get_post_likes_repo(
        post_id=post_id,
        pagination=pagination,
        session=session
    )

    return result


# =========================================================
# GET POSTS LIKED BY USER
# =========================================================

async def get_user_liked_posts(
    user_id,
    pagination: LikeCursorPagination,
    session: AsyncSession
):

    # No transaction needed.
    # Pure read query.

    result = await get_user_liked_posts_repo(
        user_id=user_id,
        pagination=pagination,
        session=session
    )

    return result


