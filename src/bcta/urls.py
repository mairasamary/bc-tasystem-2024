from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from django.views.static import serve

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="dashboard", permanent=False)),
    path("", include("main.urls")),
    path("admin/", admin.site.urls),
    path("users/", include("users.urls")),
    path("oauth/", include("django_gauth.urls")),
]
if settings.DEBUG:
    urlpatterns += [re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT})]
