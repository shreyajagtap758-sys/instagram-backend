from server.src.repository.user import get_users_ready_for_purge, mark_user_purging
from server.src.core.db.database import session_local


#UserDeletionOrchestrator
#-Delete Likes, Comments, Follows, Notifications, Posts, Media, Hard Delete User - each worker works independently(not one transaction)
#each deletion is idempotent = delete likes - crash - restart.

BATCH_SIZE = 100

async def run_user_purge_scheduler():

    while True:
        async with session_local() as session: #not get_session, because these don't get call request, these simply need to execute

            users = await get_users_ready_for_purge(
                limit=BATCH_SIZE,
                session=session
            )
        if not users:
            break

        for user in users:
            try:
                async with session_local() as session:
                    async with session.begin():

                        updated = await mark_user_purging(
                            user_id=user.id,
                            session=session
                        )
                    if not updated:
                        continue
                # Phase 4
                # Deletion orchestrator goes here.

            except Exception:
                # logger later
                continue