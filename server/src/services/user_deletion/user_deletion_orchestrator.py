from server.src.services.user_deletion.workers import (
    delete_user_likes,
    delete_user_follows,
    delete_user_posts,
    hard_delete_user,
)

PURGE_PIPELINE = (
    delete_user_likes,
    delete_user_follows,
    delete_user_posts,
    hard_delete_user,
)

async def run_user_deletion_orchestrator(user_id):

    for step in PURGE_PIPELINE:
        await step(user_id=user_id)

# flow = when user requests deletion and doesnt restore within 30 days
# user_purge_scheduler runs at its own, it gives all the accounts ready to purge/delete
# now run_user_deletion_orchestration runs, here delete_user_likes runs first, after completing, follows delete, post, then hard delete user