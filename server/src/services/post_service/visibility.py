from server.src.error_handling.exceptions.postException import PrivateContent
from server.src.utils.enums import Visibility
from server.src.repository.follow import is_following_repo

#this is used in single endpoints like get a post-> if private then raise private content
async def validate_post_visibility(post, author, viewer, session):
    allowed = await can_view_post(post=post,author=author,viewer=viewer,session=session)

    if not allowed:
        raise PrivateContent()


#this is used when 9 post -> public and 1-> private, so return 9 post instead raising privatecontent()
async def can_view_post(
    post,
    author,
    viewer,
    session
):

    if viewer and str(author.id) == str(viewer.id):
        return True #owner always allowed

    if not author.is_private:
        return True # public acct

    if not viewer: # private acct + anonymous user
        return False

    follows = await is_following_repo( #private acct + approved follower
        follower_id=viewer.id,
        following_id=author.id,
        session=session
    )

    return follows