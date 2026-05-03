from server.src import models


ALLOWED_MEDIA_TYPES = {"image", "video", "text"}
ALLOWED_VISIBILITY = {"public", "private", "followers_only"}



async def create_post_repo(session, post_obj: models.Post):
    pass



