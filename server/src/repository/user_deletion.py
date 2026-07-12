from sqlalchemy import select, delete, or_, and_
from sqlalchemy.orm import selectinload

from server.src.models.users import USER_STATUS_PURGING
from server.src import models


DELETE_BATCH_SIZE = 1000
POST_DELETE_BATCH_SIZE = 100


async def get_user_like_chunk(
    user_id,
    session,
    limit=DELETE_BATCH_SIZE
):
    result = await session.execute(
        select(
            models.PostLike.id,
            models.PostLike.post_id
        )
        .where(models.PostLike.user_id == user_id)
        .limit(limit)
    )

    return result.all()


async def delete_like_chunk(
    like_ids,
    session
):
    if not like_ids:
        return

    await session.execute(
        delete(models.PostLike)
        .where(models.PostLike.id.in_(like_ids))
    )


async def get_user_follow_chunk(user_id, session, limit=DELETE_BATCH_SIZE):
    result = await session.execute(
        select(models.Follow.id)
        .where(
            or_(
                models.Follow.follower_id == user_id,
                models.Follow.following_id == user_id,
            )
        )
        .limit(limit)
    )

    return result.scalars().all()

async def delete_follow_chunk(follow_ids, session):
    if not follow_ids:
        return

    await session.execute(
        delete(models.Follow)
        .where(models.Follow.id.in_(follow_ids))
    )

async def get_user_post_chunk(
    user_id,
    session,
    limit=POST_DELETE_BATCH_SIZE
):
    result = await session.execute(
        select(models.Post)
        .options(
            selectinload(models.Post.media)
        )
        .where(
            models.Post.author_id == user_id
        )
        .limit(limit)
    )

    return result.scalars().all()

async def hard_delete_user_repo(user, session):
    await session.delete(user)

async def get_user_for_hard_delete(user_id, session):
    result = await session.execute(
        select(models.User)
        .where(
            and_(
                models.User.id == user_id,
                models.User.status == USER_STATUS_PURGING
            )
        )
    )

    return result.scalar_one_or_none()
