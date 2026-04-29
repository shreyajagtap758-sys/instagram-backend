from sqlalchemy.exc import IntegrityError


from server.src.repository.follow import (
    insert_follow,
    increment_follower_count,
    increment_following_count,
    decrement_follower_count,
    decrement_following_count,
    delete_follow,
    get_followers_repo,
    get_following_repo,
    check_user_active
)
from server.src.error_handling.exceptions.followExceptions import SelfFollow
from server.src.error_handling.exceptions.userExceptions import UserNotFound


async def follow_user(follower_id, following_id, session):
    if follower_id == following_id:
        raise SelfFollow()

    user = await check_user_active(following_id, session)
    if not user:
        raise UserNotFound()

    try:
        if not session.in_transaction():
            await session.begin()

        await insert_follow(follower_id, following_id, session)

        await increment_follower_count(following_id, session)
        await increment_following_count(follower_id, session)

        await session.commit()

        return {"status" : "followed successfully"}

    except Exception as e:
        await session.rollback()
        raise e


async def unfollow_user(follower_id, following_id, session):

    try:
        if not session.in_transaction():
            await session.begin()

        rowcount= await delete_follow(follower_id,following_id,session)

        if rowcount > 0:  # meaning rowcount increased, relation was existing, so we deleted it
            await decrement_following_count(follower_id,session)
            await decrement_follower_count(following_id, session)

            await session.commit()
            return {"status": "Unfollowed Successfully"}

    except Exception as e:
        await session.rollback()
        raise e


async def get_following(session, user_id, last_id=None, limit=20, last_created_at=None, snapshot_time=None):
    user = await check_user_active(user_id, session)
    if not user:
        raise UserNotFound()

    rows, snapshot_time = await get_following_repo(session, user_id, last_id, limit, last_created_at, snapshot_time)

    data = [row.following_id for row in rows]

    next_cursor = None
    if rows:
        last = rows[-1]
        next_cursor = {
            "last_id" : last.following_id,
            "last_created_at" : last.created_at,
            "snapshot_time" : last.snapshot_time
        }

    return {
        "data" : data,
        "next_cursor": next_cursor
    }


async def get_followers(session, user_id, last_id=None, limit=20, last_created_at=None, snapshot_time=None):
    user = await check_user_active(user_id, session)
    if not user:
        raise UserNotFound()

    rows, snapshot_time = await get_followers_repo(session, user_id, last_id, limit, last_created_at, snapshot_time)
# returns rows=list of follow objects, and snapshot=freezing boundary

    data = [row.follower_id for row in rows]
# extract only follower_id from rows list[follower_id=x,created_at=x...]

    next_cursor = None
    if rows: # if current page has data exist, then we can check next page
        last = rows[-1]
        next_cursor = {"last_id": last.follower_id,
                      "last_created_at": last.created_at,
                      "snapshot_time": snapshot_time
                       }

    return {
        "data": data,  # return curr data
        "next_cursor": next_cursor # and next page pointer
    }


