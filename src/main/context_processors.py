from main.models import Notification


def notifications(request):
    if not request.user.is_authenticated:
        return {
            "navbar_notifications": [],
            "navbar_unread_notifications_count": 0,
        }

    qs = Notification.objects.filter(user=request.user).order_by("-created_at")
    return {
        "navbar_notifications": list(qs[:8]),
        "navbar_unread_notifications_count": qs.filter(is_read=False).count(),
    }
