from django.shortcuts import redirect
from django.urls import reverse


class ProfileWelcomeMiddleware:
    """
    New students must complete the one-time welcome screen before using the app.
    Allowed paths: OAuth, admin, static/media assets, welcome, profile, auth endpoints.
    """

    ALLOW_PATH_PREFIXES = (
        "/oauth/",
        "/admin/",
        "/static/",
        "/media/",
        "/welcome/",
        "/profile/",
        "/users/logout/",
        "/users/login/",
        "/users/profile/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated and user.student_needs_profile_welcome():
            path = request.path
            if not any(path.startswith(p) for p in self.ALLOW_PATH_PREFIXES):
                return redirect(reverse("profile_welcome"))
        return self.get_response(request)
