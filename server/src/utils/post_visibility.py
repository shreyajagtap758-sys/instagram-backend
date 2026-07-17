from server.src.repository.follow import is_following_repo
from server.src.error_handling.exceptions.postException import PrivateContent
from server.src.utils.user_visibility import is_user_hidden


#this is used in single endpoints like get a post-> if private then raise private content
async def validate_post_visibility(post, author, viewer, session):
    allowed = await can_view_account(post=post,author=author,viewer=viewer,session=session)

    if not allowed:
        raise PrivateContent()


#this is used when 9 post -> public and 1-> private(total=10 posts), so return 9 post instead raising privatecontent()
#post visibility now also depends on user visibility(active/suspended)
async def can_view_account(
    post,
    author,
    viewer,
    session
):
    if viewer and str(author.id) == str(viewer.id):
        return True #owner always allowed

    if is_user_hidden(author):
        return False #author not active, content is not visible now

    if not author.is_private:
        return True # public acct

    if not viewer: # private acct + anonymous user
        return False

    if is_user_hidden(viewer):
        return False # if viewer is not active

    follows = await is_following_repo( #private acct + approved follower
        follower_id=viewer.id,
        following_id=author.id,
        session=session
    )

    return follows