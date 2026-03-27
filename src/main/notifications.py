from main.models import Notification


def create_notification(user, title, target_url="/"):
    """Persist a notification for a user."""
    if not user:
        return
    Notification.objects.create(
        user=user,
        title=title[:255],
        target_url=target_url or "/",
    )
