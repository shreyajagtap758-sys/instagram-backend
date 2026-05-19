from server.src.services.post_service.post_storage import delete_object
from server.src.repository.posts import get_expired_pending_upload_repo, delete_media_upload_repo, get_deleted_posts_repo, hard_delete_post_repo


async def cleanup_uploads(session):  # this cleans up upload urls + object_key, when user reuest upload url+object key,but never create_post
    uploads = await get_expired_pending_upload_repo(session)

    for upload in uploads:
        try:
            delete_object(upload.object_key)
        except Exception:
            continue  #deleting 50 and 30th deletion fails, should not roll back previous 29 deletions

        await delete_media_upload_repo(upload, session)

    await session.commit()


async def cleanup_deleted_posts(session):  # this hard deletes(post+media) the soft deleted post after 30 days
    posts = await get_deleted_posts_repo(session)
    for post in posts:
        storage_delete_failed = False #if any media object deletion fails : dont delete db post row for that

        for media in post.media:
            try:
                delete_object(media.object_key)
            except Exception:
                storage_delete_failed = True
                break

        if storage_delete_failed:
            continue

        await hard_delete_post_repo(post, session)

    await session.commit()
