from sqlalchemy import delete, and_, select, or_
from datetime import timedelta


from server.src import models
from server.src.core.minio_storage import minio_client, BUCKET_NAME


async def create_post_repo(data, user_id: str, session):
    post = models.Post(
        user_id=user_id,
        caption=data.caption,
        visibility=data.visibility,
        status="published",
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
    await session.commit()

    return post


async def delete_post_repo(post_id:str, user_id, session):
    result = await session.execute(
        delete(models.Post).
        where(
            and_(
                models.Post.id == post_id,
                models.Post.user_id == user_id,
                models.Post.status != "deleted"
            )
        )
        .values(status="deleted")
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
            models.Post.status != "deleted"
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
    media = media_result.scalars.all()
    return post, media


async def get_user_posts_repo(user_id, pagination, session):
    query = select(models.Post).where(
        and_(
            models.Post.user_id == user_id,
            models.Post.status != "deleted",
            models.Post.created_at <= pagination.snapshot_time
        )
    )
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
        order_by(pagination.limit)
    )
    result = await session.execute(query)

    return result.scalars().all()


def generate_presigned_upload_url(object_key: str):
    return minio_client.presigned_put_object(
        bucket_name=BUCKET_NAME,
        object_name=object_key,
        expires=timedelta(minutes=10)
    )
