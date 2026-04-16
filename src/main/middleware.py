from django.shortcuts import redirect
from django.urls import reverse


class ProfileWelcomeMiddleware:
    """
    New students must complete the one-time welcome screen before using the app.

    After the welcome step, students are also blocked from navigating the rest of
    the site until their student profile is complete (including Grad Year).

    Allowed paths: OAuth, admin, static/media assets, welcome, profile, auth endpoints.
    """

    ALLOW_PATH_PREFIXES = (
        "/oauth/",
        "/admin/",
        "/static/",
        "/media/",
        "/welcome/",
        "/help/",
        "/profile/",
        "/users/logout/",
        "/users/login/",
        "/users/profile/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated:
            # Professors/admins/staff bypass this onboarding gating.
            if user.is_professor or user.is_superuser or user.is_staff:
                return self.get_response(request)

            path = request.path

            # Step 1: one-time welcome screen
            if user.student_needs_profile_welcome():
                if not any(path.startswith(p) for p in self.ALLOW_PATH_PREFIXES):
                    return redirect(reverse("profile_welcome"))
                return self.get_response(request)

            # Step 2: required profile fields
            if not user.has_complete_profile_for_apply():
                if not any(path.startswith(p) for p in self.ALLOW_PATH_PREFIXES):
                    return redirect(reverse("student_profile"))
        return self.get_response(request)
