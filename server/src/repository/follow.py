from sqlalchemy import delete, select, func, or_, and_, update

from server.src import models


async def insert_follow(follower_id, following_id, session):
    follow = models.Follow(
        follower_id=follower_id,
        following_id=following_id
    )
    session.add(follow)


async def increment_following_count(user_id, session):
    await session.execute(
        update(models.User)
        .where(models.User.id == user_id)
        .values(following_count=models.User.following_count + 1)
    )


async def increment_follower_count(user_id, session):
    await session.execute(
        update(models.User)
        .where(models.User.id == user_id)
        .values(follower_count=models.User.follower_count + 1)
    )


async def delete_follow(follower_id, following_id, session):
    result = await session.execute(
        delete(models.Follow).where(
            models.Follow.follower_id == follower_id,
            models.Follow.following_id == following_id
        )
    )
    return result.rowcount


async def decrement_following_count(user_id, session):
    await session.execute(
        models.User.__table__.update()
        .where(and_(
            models.User.id == user_id,
            models.User.following_count > 0  # Safety Check
        ))
        .values(following_count=models.User.following_count - 1)
    )


async def decrement_follower_count(user_id, session):
    await session.execute(
        models.User.__table__.update()
        .where(and_(
            models.User.id == user_id,
            models.User.follower_count > 0  # Safety Check
        ))
        .values(follower_count=models.User.follower_count - 1)
    )


async def get_followers_repo(session, user_id, last_id=None, limit=20, last_created_at=None, snapshot_time=None):

    if snapshot_time is None: # for first request
        result = await session.execute(
            select(func.max(models.Follow.created_at)).
            where(models.Follow.following_id == user_id)
        )
        snapshot_time = result.scalar()  # store latest(max) value(created_at)-> shows data only till latest follow added

        if snapshot_time is None:
            return [], None

    statement = (select(models.Follow).
                where(models.Follow.following_id == user_id, # get user followers
                 models.Follow.created_at <= snapshot_time) # data till latest snapshot
                 )

    if last_created_at is not None and last_id is not None:  # next page request

        statement = statement.where(
            or_(
                models.Follow.created_at < last_created_at,  # show next follow
                and_(
                    models.Follow.created_at == last_created_at,  # if two latest id followed at same time
                    models.Follow.follower_id < last_id # so deicide by follow_id
                )
            )
        )

    statement = statement.order_by(models.Follow.created_at.desc(),
        models.Follow.follower_id.desc()).limit(limit) # order by time, then id, and limit = max 20 follower show in one page

    result = await session.execute(statement)
    return result.scalars().all(), snapshot_time


async def get_following_repo(session, user_id, last_id=None, limit=20, last_created_at=None, snapshot_time=None):
    # first request → snapshot fix
# snapshot_time= let say user opened following list at 10:20, snapshot time is now 10:20 for first page= new_following added after 10:20 in first page gets ignored
    if snapshot_time is None:
        result = await session.execute(
            select(func.max(models.Follow.created_at)).where(
                models.Follow.follower_id == user_id
            )
        )
        snapshot_time = result.scalar()

        if snapshot_time is None:
            return [], None

    stmt = select(models.Follow).where(
        models.Follow.follower_id == user_id,
        models.Follow.created_at <= snapshot_time
    )

    # cursor condition
    if last_created_at is not None and last_id is not None:
        stmt = stmt.where(
            or_(
                models.Follow.created_at < last_created_at,
                and_(
                    models.Follow.created_at == last_created_at,
                    models.Follow.following_id < last_id
                )
            )
        )

    stmt = stmt.order_by(
        models.Follow.created_at.desc(),
        models.Follow.following_id.desc()
    ).limit(limit)

    result = await session.execute(stmt)
    return result.scalars().all(), snapshot_time


async def check_user_active(user_id, session):
    # Return the full User model so that visibility utilities can access attributes like `status`, `is_private`, and `id`
    stmt = (
        select(models.User)
        .where(
            models.User.id == user_id,
            models.User.is_deleted == False,
            models.User.is_active == True,
            models.User.status == "active",
        )
        .with_for_update()
    )
    result = await session.execute(stmt)
    # `scalar_one_or_none` returns the User instance or None
    return result.scalar_one_or_none()

async def lock_user(
    follower_id,
    following_id,
    session
):
    first_id, second_id = sorted(
        [follower_id, following_id]
    )

    await session.execute(
        select(models.User.id)
        .where(
            models.User.id.in_([first_id, second_id])
        )
        .order_by(models.User.id)
        .with_for_update()
    )

async def is_following_repo(
    follower_id,
    following_id,
    session
):
    result = await session.execute(
        select(models.Follow).where(
            and_(
                models.Follow.follower_id == follower_id,
                models.Follow.following_id == following_id,
                models.Follow.accepted.is_(True),
                models.Follow.status == "active",
                models.Follow.deleted_at.is_(None)
            )
        )
        .limit(1)
    )

    return result.scalar_one_or_none() is not None
