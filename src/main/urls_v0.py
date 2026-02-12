from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home_v0'),
    path('courses/', include('courses.urls')),
    path('applications/', include('applications.urls')),
    path('offers/', include('offers.urls')),
]
