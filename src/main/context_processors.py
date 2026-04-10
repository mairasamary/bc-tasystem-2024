from main.models import Notification


def navbar_profile_photo(request):
    """Expose whether the logged-in user has a student profile photo (for navbar avatar)."""
    if not request.user.is_authenticated:
        return {"navbar_show_profile_photo": False, "navbar_onboarding_complete": True, "navbar_onboarding_steps_completed": 0}
    from users.models import StudentProfile

    try:
        profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        return {"navbar_show_profile_photo": False, "navbar_onboarding_complete": False, "navbar_onboarding_steps_completed": 0}
    return {
        "navbar_show_profile_photo": bool(profile.profile_photo),
        "navbar_onboarding_complete": profile.onboarding_complete,
        "navbar_onboarding_steps_completed": profile.onboarding_steps_completed,
    }


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
