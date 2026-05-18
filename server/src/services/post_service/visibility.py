from server.src.error_handling.exceptions.postException import PrivateContent
from server.src.utils.enums import Visibility


def validate_post_visibility(post, user):
    if post.visibility == Visibility.PRIVATE:
        if not user or str(post.user_id) != str(user.id):
            raise PrivateContent()