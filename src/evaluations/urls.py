from django.urls import path

from . import views

app_name = "evaluations"

urlpatterns = [
    path("", views.evaluation_list, name="list"),
    path("create/", views.evaluation_create, name="create"),
    path("<int:pk>/edit/", views.evaluation_edit, name="edit"),
    path("<int:pk>/delete/", views.evaluation_delete, name="delete"),
]
