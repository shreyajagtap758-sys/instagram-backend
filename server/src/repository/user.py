from datetime import datetime, timezone, timedelta
from sqlalchemy import select, func, update, and_

from server.src import models
from server.src.models.users import USER_STATUS_PENDING_DELETION, USER_STATUS_PURGING


RESTORE_WINDOW_DAYS = 30
LIVE_USER_STATUS = {"active"}


async def get_user_by_id(user_id, session):
    result = await session.execute(select(models.User).where(models.User.id == user_id))

    return result.scalar_one_or_none() #returns user id of any status(suspended/active)

async def get_live_user_by_id(user_id, session):
    result = await session.execute(select(models.User).
            where(models.User.id == user_id,
                models.User.status.in_(LIVE_USER_STATUS)
            )
    )
    return result.scalar_one_or_none() # returns only live/active users(not suspended)

async def get_user_by_email(user_email, session):
    statement = select(models.User).where(models.User.email == user_email)
    result = await session.execute(statement)

    return result.scalar_one_or_none()

async def user_creation(new_user, session):
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user

async def username_exists(username, session):
    result = await session.execute(
        select(models.User).where(models.User.username == username)
    )
    return result.scalars().first()

async def get_active_sessions_count(user_id:str, session):
    result = await session.execute(
        select(func.count()).select_from(models.RefreshToken).
        where(models.RefreshToken.user_id == user_id,
              models.RefreshToken.revoked == False)
    )
    return result.scalar_one()

async def revoke_oldest_session(user_id: str, session):
    result = await session.execute(
        select(models.RefreshToken.id).
        where(models.RefreshToken.user_id == user_id,
        models.RefreshToken.revoked == False).
        order_by(models.RefreshToken.created_at.asc()).
        limit(1)
    )
    oldest = result.scalar_one_or_none()
    if oldest:
        await session.execute(
            update(models.RefreshToken)
            .where(models.RefreshToken.id == oldest)
            .values(revoked=True)
        )

async def get_user_for_deletion_update(user_id,session):
    # Lock the user row so delete/restore transitions cannot race each other.
    result = await session.execute(
        select(models.User)
        .where(models.User.id == user_id)
        .with_for_update()
    )
    return result.scalar_one_or_none()


async def mark_user_pending_deletion(user,session):
    """
    Transition current user into pending_deletion.
    Save previous status so restore can return to it.
    """
    now = datetime.now(timezone.utc)
    scheduled_for = now + timedelta(days=RESTORE_WINDOW_DAYS)

    stmt = (
        update(models.User)
        .where(models.User.id == user.id)
        .values(
            pre_deletion_status=user.status,
            status="pending_deletion",
            deleted_at=now,
            deletion_scheduled_for=scheduled_for,
            purge_started_at=None,
            purged_at=None
        )
        .returning(
            models.User.status,
            models.User.deleted_at,
            models.User.deletion_scheduled_for
        )
    )

    result = await session.execute(stmt)
    row = result.one()

    return {
        "status": row.status,
        "deleted_at": row.deleted_at,
        "deletion_scheduled_for": row.deletion_scheduled_for
    }


async def restore_pending_deletion_user(user,session):
    """
    Restore a pending_deletion user back to the previous status.
    If previous status is missing, default to active.
    """
    restored_status = user.pre_deletion_status or "active"

    stmt = (
        update(models.User)
        .where(models.User.id == user.id)
        .values(
            status=restored_status,
            pre_deletion_status=None,
            deleted_at=None,
            deletion_scheduled_for=None,
            purge_started_at=None,
            purged_at=None
        )
        .returning(models.User.status)
    )

    result = await session.execute(stmt)
    row = result.one()

    return {
        "status": row.status
    }


async def create_user_deletion_audit_event(user_id,event_type,session):
    audit_row = models.UserDeletionAudit(
        user_id=user_id,
        event_type=event_type
    )
    session.add(audit_row)

async def mark_user_purging(
    user_id,
    session
):
    result = await session.execute(
        update(models.User)
        .where(
            and_(
                models.User.id == user_id,
                models.User.status == USER_STATUS_PENDING_DELETION
            )
        )
        .values(
            status=USER_STATUS_PURGING,
            purge_started_at=datetime.now(timezone.utc)
        )
        .returning(models.User.id)
    )

    return result.scalar_one_or_none()

async def get_users_ready_for_purge(
    limit,
    session
):
    result = await session.execute(
        select(models.User)
        .where(
            and_(
                models.User.status == USER_STATUS_PENDING_DELETION,
                models.User.deletion_scheduled_for <= datetime.now(timezone.utc)
            )
        )
        .order_by(models.User.deletion_scheduled_for)
        .limit(limit)
        .with_for_update(skip_locked=True)
        # if user A is ready to purge, schedules for purging are moving at same time, so multiple schedules may work on same user, to avoid that, we use skip_locked
        #meaning if user a is given to scheduler A, scheduler b sees it as locked, and grabs user b,c..
    )

    return result.scalars().all()

