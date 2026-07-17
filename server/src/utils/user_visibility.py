from server.src.models.users import USER_STATUS_PENDING_DELETION, USER_STATUS_PURGING


def is_user_hidden(user) -> bool:
    """
    A user is product-visible only if lifecycle status is live.
    pending_deletion / purging must be treated as invisible.
    """
    if not user:
        return True

    return user.status in {USER_STATUS_PENDING_DELETION, USER_STATUS_PURGING}
