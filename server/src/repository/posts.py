from sqlalchemy import delete, and_, select, or_, update
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone, timedelta

from server.src.utils.enums import PostStatus, UploadStatus
from server.src import models


async def create_post_repo(data, user_id: str, session):
    post = models.Post(
        author_id=user_id,
        caption=data.caption,
        visibility=data.visibility,
        status=PostStatus.PUBLISHED,
    )

    session.add(post)
    await session.flush()

    media_objects = [
        models.PostMedia(
            post_id=post.id,
            object_key=m.object_key,
            media_type=m.media_type,
            order_index=idx,
        )
        for idx, m in enumerate(data.media)
    ]

    session.add_all(media_objects)

    return post


async def delete_post_repo(post_id:str, user_id, session):
    result = await session.execute(
        update(models.Post).
        where(
            and_(
                models.Post.id == post_id,
                models.Post.author_id == user_id,
                models.Post.status != PostStatus.DELETED
            )
        )
        .values(status=PostStatus.DELETED, deleted_at=datetime.now(timezone.utc))
        .returning(models.Post.id)
    )
    deleted = result.scalar_one_or_none()

    if deleted:
        await session.commit()

    return deleted


async def get_post_with_media_repo(post_id, session):
    post_result = await session.execute(
        select(models.Post).
        where(and_(
            models.Post.id == post_id,
            models.Post.status != PostStatus.DELETED
        ))
    )
    post = post_result.scalar_one_or_none()

    if not post:
        return None, []

    media_result = await session.execute(
        select(models.PostMedia).
        where(models.PostMedia.post_id == post.id).
        order_by(models.PostMedia.order_index)
    )

    media = media_result.scalars().all()
    return post, media


async def get_user_posts_repo(user_id, pagination, session):
    query = (select(models.Post).options(selectinload(models.Post.media),selectinload(models.Post.author)).  #get efficient post+medias in 2 queries
    where(
        and_(
            models.Post.author_id == user_id,
            models.Post.status != PostStatus.DELETED,
            models.Post.created_at <= pagination.snapshot_time
        )
    ))
    if pagination.last_created_at and pagination.last_id:
        query = query.where(
            or_(
                models.Post.created_at < pagination.last_created_at,
                and_(
                    models.Post.created_at == pagination.last_created_at,
                    models.Post.id < pagination.last_id
                )
            )
        )
    query = (
        query.order_by(models.Post.created_at.desc(), models.Post.id.desc()).
        limit(pagination.limit)
    )
    result = await session.execute(query)

    return result.scalars().all()


async def create_media_upload_repo(user_id, object_key, media_type, session):
    upload = models.MediaUpload(
        author_id=user_id,object_key=object_key,media_type=media_type,status=UploadStatus.PENDING
    )
    session.add(upload)
    await session.commit()
    return upload


async def get_pending_upload_repo(
    object_key,
    user_id,
    session
):
    result = await session.execute(
        select(models.MediaUpload).where(
            and_(
                models.MediaUpload.object_key == object_key,
                models.MediaUpload.author_id == user_id,
                models.MediaUpload.status == UploadStatus.PENDING
            )
        )
    )
    return result.scalar_one_or_none()

async def mark_upload_attached_repo(
    object_key,
    session
):
    result = await session.execute(
        select(models.MediaUpload).where(
            models.MediaUpload.object_key == object_key
        )
    )
    upload = result.scalar_one_or_none()
    if upload:
        upload.status = UploadStatus.ATTACHED

    await session.flush() #create_post_repo already commits


async def get_expired_pending_upload_repo(session):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

    result = await session.execute(
        select(models.MediaUpload).where(
            and_(
                models.MediaUpload.status == UploadStatus.PENDING,
                models.MediaUpload.create_at < cutoff
            )
        )
    )
    return result.scalars().all()


async def delete_media_upload_repo(upload, session):
    await session.delete(upload)


async def update_post_repo(post_id, user_id, update_data, session):
    result = await session.execute(
        update(models.Post).
        where(
            and_(
                models.Post.id == post_id,
                models.Post.author_id == user_id,
                models.Post.status != PostStatus.DELETED
            )
        )
        .values(**update_data).returning(models.Post)
    )
    return result.scalar_one_or_none()

async def get_deleted_posts_repo(session):
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)

    result = await session.execute(
        select(models.Post).options(selectinload(models.Post.media)).
        where(and_(
            models.Post.status == PostStatus.DELETED,
            models.Post.deleted_at < cutoff
        ))
    )
    return result.scalars().all()

async def hard_delete_post_repo(post, session):
    await session.delete(post)

async def get_post_by_id_repo(post_id,session):
    result = await session.execute(
        select(models.Post)
        .where(
            and_(
                models.Post.id == post_id,
                models.Post.status != PostStatus.DELETED
            )
        )
    )
    return result.scalar_one_or_none()


