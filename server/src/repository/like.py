from sqlalchemy import (select,and_,or_,update,delete)
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import selectinload


from server.src import models
from server.src.schemas.like import LikeCursorPagination
from server.src.utils.enums import PostStatus


async def like_post_repo(post_id,user_id,session):
    # Try inserting like row.
    # If same user already liked same post,
    # db ignores insert because of UNIQUE(post_id, user_id).
    insert_statement = (
        insert(models.PostLike)
        .values(
            post_id=post_id,
            user_id=user_id
        )
        .on_conflict_do_nothing(
            index_elements=["post_id", "user_id"]  #ignore insert instead of crashing.
        )
        .returning(models.PostLike.id)  #if insert=return inserted row is else return none
    )
    insert_result = await session.execute(insert_statement)

    # If insert happens:
    # returns inserted row id
    # Else:
    # returns None
    inserted_like_id = insert_result.scalar_one_or_none()

    # Already liked case.
    # No counter increment should happen(duplication)
    if not inserted_like_id:

        # Fetch current count only.
        existing_like_count_statement = (
            select(models.Post.like_count)
            .where(models.Post.id == post_id)
        )

        existing_like_count_result = await session.execute(
            existing_like_count_statement
        )

        existing_like_count = (
            existing_like_count_result.scalar_one()
        )

        return {
            "liked": True,
            "like_count": existing_like_count
        }

    # Insert succeeded.
    # Atomically increment like_count in DB.
    # This avoids race conditions from:
    # post.like_count += 1
    increment_like_count_statement = (
        update(models.Post)
        .where(models.Post.id == post_id)
        .values(
            like_count=models.Post.like_count + 1
        )
        .returning(models.Post.like_count) # returns updated value
    )
    increment_result = await session.execute( # run update
        increment_like_count_statement
    )
    #get new count.
    updated_like_count = increment_result.scalar_one()

    return {
        "liked": True,
        "like_count": updated_like_count
    }

async def unlike_post_repo(
    post_id,
    user_id,
    session
):

    # Try deleting like row.
    # If row existed:
    # DELETE succeeds and returns deleted row id.
    # If already deleted:
    # returns None.
    delete_statement = (
        delete(models.PostLike)
        .where(
            and_(
                models.PostLike.post_id == post_id,
                models.PostLike.user_id == user_id
            )
        )
        .returning(models.PostLike.id)
    )
    delete_result = await session.execute(
        delete_statement
    )
    deleted_like_id = (
        delete_result.scalar_one_or_none()
    )

    # Already unliked.
    # Return current count without decrementing.
    if not deleted_like_id:
        existing_count_statement = (
            select(models.Post.like_count)
            .where(models.Post.id == post_id)
        )
        existing_count_result = await session.execute(
            existing_count_statement
        )
        existing_like_count = (
            existing_count_result.scalar_one()
        )

        return {
            "liked": False,
            "like_count": existing_like_count
        }

    # Decrement counter atomically.
    decrement_statement = (
        update(models.Post)
        .where(
            and_(
                models.Post.id == post_id,
                models.Post.like_count > 0
            )
        )
        .values(
            like_count=models.Post.like_count - 1
        )
        .returning(models.Post.like_count)
    )

    decrement_result = await session.execute(
        decrement_statement
    )

    updated_like_count = (
        decrement_result.scalar_one()
    )

    return {
        "liked": False,
        "like_count": updated_like_count
    }

async def get_user_liked_posts_repo(
    user_id,
    pagination,
    session
):

    query = (
        select(models.PostLike)
        .join(models.Post)
        .options(
            selectinload(models.PostLike.post)
        )
        .where(
            and_(
                models.PostLike.user_id == user_id,
                models.PostLike.created_at <= pagination.snapshot_time,
                models.Post.status != PostStatus.DELETED
            )
        )
    )

    if pagination.last_created_at and pagination.last_id:

        query = query.where(
            or_(

                models.PostLike.created_at
                < pagination.last_created_at,

                and_(
                    models.PostLike.created_at
                    == pagination.last_created_at,

                    models.PostLike.id
                    < pagination.last_id
                )
            )
        )

    query = (
        query
        .order_by(
            models.PostLike.created_at.desc(),
            models.PostLike.id.desc()
        )
        .limit(pagination.limit + 1)
    )

    result = await session.execute(query)

    rows = result.scalars().all()

    has_more = len(rows) > pagination.limit

    if has_more:
        rows = rows[:-1]

    next_cursor = None

    if rows:
        last_row = rows[-1]

        next_cursor = {
            "last_created_at": last_row.created_at,
            "last_id": str(last_row.id)
        }

    return {
        "items": rows,
        "has_more": has_more,
        "next_cursor": next_cursor
    }

async def get_post_likes_repo(
    post_id,
    pagination: LikeCursorPagination,
    session
):

    query = (
        select(models.PostLike)
        .options(
            selectinload(models.PostLike.user)
        )
        .where(
            and_(
                models.PostLike.post_id == post_id,
                models.PostLike.created_at <= pagination.snapshot_time
            )
        )
    )

    # cursor pagination
    if pagination.last_created_at and pagination.last_id:

        query = query.where(
            or_(

                models.PostLike.created_at
                < pagination.last_created_at,

                and_(
                    models.PostLike.created_at
                    == pagination.last_created_at,

                    models.PostLike.id
                    < pagination.last_id
                )
            )
        )

    query = (
        query
        .order_by(
            models.PostLike.created_at.desc(),
            models.PostLike.id.desc()
        )
        .limit(pagination.limit+1)
    )

    result = await session.execute(query)

    rows = result.scalars().all()
    has_more = len(rows) > pagination.limit

    if has_more:
        rows = rows[:-1]

    next_cursor = None

    if rows:
        last_row = rows[-1]

        next_cursor = {
            "last_created_at": last_row.created_at,
            "last_id": str(last_row.id)
        }

    return {
        "items": rows,
        "has_more": has_more,
        "next_cursor": next_cursor
    }

