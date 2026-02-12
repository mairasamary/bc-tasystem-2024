from django.urls import path, re_path
from django.views.generic import RedirectView
from .views import ProfileView, StudentProfileView, serve_resume, serve_cv, serve_profile_photo
from django.contrib.auth import views as auth_views

app_name = 'users'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    re_path(r'^update/(?P<pk>[0-9a-f-]+)/$', ProfileView.as_view(), name='profile'),
    path('profile/', RedirectView.as_view(pattern_name='student_profile_v2', permanent=False), name='student_profile'),
    path('profile/resume/', serve_resume, name='serve_resume'),
    path('profile/cv/', serve_cv, name='serve_cv'),
    path('profile/photo/', serve_profile_photo, name='serve_profile_photo'),
]
