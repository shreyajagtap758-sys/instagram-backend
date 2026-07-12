from server.src.database import session_local

from server.src.repository.posts import hard_delete_post_repo
from server.src.repository.user_deletion import (
    get_user_like_chunk,
    delete_like_chunk,
    get_user_follow_chunk,
    delete_follow_chunk,
    get_user_post_chunk,
    get_user_for_hard_delete,
    hard_delete_user_repo
)

from server.src.workers.like_counter_reconciliation_job import (
    repair_post_like_count,
)
from services.post_service.post_storage import delete_object


DELETE_BATCH_SIZE = 1000
POST_PURGE_BATCH_SIZE = 100


async def delete_user_likes(user_id):

    affected_posts = set()

    while True:

        async with session_local() as session:

            async with session.begin():

                rows = await get_user_like_chunk(
                    user_id=user_id,
                    session=session,
                    limit=DELETE_BATCH_SIZE
                )

                if not rows:
                    break

                like_ids = []
                for row in rows:
                    like_ids.append(row.id)
                    affected_posts.add(row.post_id)

                await delete_like_chunk(
                    like_ids=like_ids,
                    session=session
                )

    async with session_local() as session:

        async with session.begin():

            for post_id in affected_posts:
                await repair_post_like_count(
                    post_id=post_id,
                    session=session
                )

async def delete_user_follows(user_id):

    while True:

        async with session_local() as session:

            async with session.begin():

                follow_ids = await get_user_follow_chunk(
                    user_id=user_id,
                    session=session,
                    limit=DELETE_BATCH_SIZE,
                )

                if not follow_ids:
                    break

                await delete_follow_chunk(
                    follow_ids=follow_ids,
                    session=session,
                )

async def delete_user_posts(user_id):

    while True:

        async with session_local() as session:

            posts = await get_user_post_chunk(
                user_id=user_id,
                session=session,
                limit=POST_PURGE_BATCH_SIZE
            )

            if not posts:
                break

            async with session.begin():

                for post in posts:

                    storage_failed = False

                    for media in post.media:

                        try:
                            delete_object(media.object_key)

                        except Exception:
                            storage_failed = True
                            break

                    if storage_failed:
                        continue

                    await hard_delete_post_repo(
                        post=post,
                        session=session
                    )

async def hard_delete_user(user_id):

    async with session_local() as session:

        async with session.begin():

            user = await get_user_for_hard_delete(
                user_id=user_id,
                session=session
            )

            if not user:
                return

            await hard_delete_user_repo(
                user=user,
                session=session
            )



