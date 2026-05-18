from server.src.services.post_service.post_storage import delete_object
from server.src.repository.posts import get_expired_pending_upload_repo, delete_media_upload_repo


async def cleanup_uploads(session):
    uploads = await get_expired_pending_upload_repo(session)

    for upload in uploads:
        try:
            delete_object(upload.object_key)
        except Exception:
            continue  #deleting 50 and 30th deletion fails, should not roll back previous 29 deletions

        await delete_media_upload_repo(upload, session)

    await session.commit()