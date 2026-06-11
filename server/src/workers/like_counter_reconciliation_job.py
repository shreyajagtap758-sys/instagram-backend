#reconciliation job - system survive failures, repairs itself.
#this is build for denormalization job - like system
#calculating get likes for a post select count * is expensive for large dataset = so we do denormalization = same data (copy) stored twice
# for post.like_count(count) and postlike table(rows). if transaction fails = insert like row = 20, insert like_count = 19(counter drift) = inconsistency
#eg = re likes on post = 10, displayed = 8
#question: why not use transaction instead handling counter drift as detect drift + repair? manual mistake delete post_id: post likes deleted = now actual likes = 0, like_count still same(inconsistent). or manual update like_count = inconsistent. to avoid data becoming wrong someday = we use transaction to prevent bugs, repair everything later

#1 repair one post : count actual likes: if inconsistent: run repair,update post.like_count
#2 select all posts from like_count and actual count : return all broken posts(inconsistent from actual like_count)
#3 reconcile all : repair each and return statistics: checked: 100, drifted: 14, repaired: 14.


from sqlalchemy import select
from sqlalchemy import func
from sqlalchemy import update

from server.src import models


async def repair_post_like_count(post_id, session): #repair one post.
    actual_count_result = await session.execute(
        select(func.count(models.PostLike.id))
        .where(models.PostLike.post_id == post_id)
    )
    actual_count = actual_count_result.scalar_one() # stored = 500, actual = 503

    await session.execute(
        update(models.Post)
        .where(models.Post.id == post_id)
        .values(like_count=actual_count) # update stored = 503
    )

    return {"post_id": str(post_id),
            "actual_count": actual_count}


async def find_drifted_posts(session):
    result = await session.execute(
        select(models.Post.id,          #which post broken
               models.Post.like_count,  #what like_count is stored = denormalized
               func.count(models.PostLike.id).label("actual_like_count")) #count likes actually exists = truth
        .outerjoin(                     # eg = like_count = 20, actual_likes = 0 -> inner join(.join) = ignores 0 liked posts, outer join = keeps all posts
            models.PostLike,
            models.PostLike.post_id == models.Post.id)
        .group_by(models.Post.id)       # count like separately for each post instead combining all likes
        .having(func.count(models.PostLike.id) != models.Post.like_count)  # get all drifted post where actual count != like_count
    )

    rows = result.all()

    return [
        {
            "post_id": row.id,
            "stored_like_count": row.like_count,
            "actual_like_count": row.actual_like_count
        }
        for row in rows
    ]

async def reconcile_all_posts(session):
    drifted_posts = await find_drifted_posts(session=session)

    repaired = 0

    for post in drifted_posts:
        await repair_post_like_count(post_id=post["post_id"], session=session)

        repaired += 1

    return {
        "drifted_posts": len(drifted_posts),
        "repaired_posts": repaired
    }


