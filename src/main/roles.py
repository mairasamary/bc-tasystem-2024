"""
Which role a dual-role user is browsing as.

Only affects what is shown and which rows are scoped. Permission guards keep
using the real is_superuser / professor flags, so a user in instructor view can
still switch back and can still perform anything their account allows.
"""

ADMIN = "admin"
INSTRUCTOR = "instructor"
SESSION_KEY = "role_view"
CHOICES = (ADMIN, INSTRUCTOR)


def is_dual_role(user):
    return bool(
        getattr(user, "is_authenticated", False)
        and user.is_superuser
        and user.professor
    )


def active_role(request):
    """The chosen view, or '' for anyone who is not dual-role."""
    if not is_dual_role(getattr(request, "user", None)):
        return ""
    chosen = request.session.get(SESSION_KEY, ADMIN)
    return chosen if chosen in CHOICES else ADMIN


def acts_as_admin(request):
    user = getattr(request, "user", None)
    if not getattr(user, "is_authenticated", False):
        return False
    if is_dual_role(user):
        return active_role(request) == ADMIN
    return bool(user.is_superuser)


def acts_as_professor(request):
    user = getattr(request, "user", None)
    if not getattr(user, "is_authenticated", False):
        return False
    if is_dual_role(user):
        return active_role(request) == INSTRUCTOR
    return bool(user.is_professor)
