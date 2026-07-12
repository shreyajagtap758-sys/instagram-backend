from server.src.repository.user import get_users_ready_for_purge, mark_user_purging
from server.src.core.db.database import session_local
from server.src.services.user_deletion.user_deletion_orchestrator import run_user_deletion_orchestrator

#UserDeletionOrchestrator
#-Delete Likes, Comments, Follows, Notifications, Posts, Media, Hard Delete User - each worker works independently(not one transaction)
#each deletion is idempotent = delete likes - crash - restart.

BATCH_SIZE = 100

async def run_user_purge_scheduler():

    while True:

        async with session_local() as session:
            async with session.begin():

                users = await get_users_ready_for_purge(
                    limit=BATCH_SIZE,
                    session=session
                )

                if not users:
                    break

                claimed_user_ids = []

                for user in users:

                    updated = await mark_user_purging(
                        user_id=user.id,
                        session=session
                    )

                    if updated:
                        claimed_user_ids.append(updated)

        # Transaction committed here.
        # Locks released here.

        for user_id in claimed_user_ids:
            try:
                await run_user_deletion_orchestrator(user_id)

            except Exception:
                # logger later
                continue