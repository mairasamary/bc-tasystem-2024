from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.admin_dashboard_v2, name="dashboard_v2"),
    path("applications/", views.applications_list_v2, name="applications_v2"),
    path("offers/", views.offers_list_v2, name="offers_v2"),
    path("courses/", views.courses_list_v2, name="courses_v2"),
    path("apply/<uuid:course_id>/", views.apply_to_course_v2, name="apply_to_course_v2"),
    path("make-offer/<uuid:application_id>/", views.make_offer_v2, name="make_offer_v2"),
    path("reject-application/<uuid:application_id>/", views.reject_application_v2, name="reject_application_v2"),
    path("accept-offer/<uuid:offer_id>/", views.accept_offer_v2, name="accept_offer_v2"),
    path("decline-offer/<uuid:offer_id>/", views.decline_offer_v2, name="decline_offer_v2"),
    path("application/<uuid:application_id>/", views.application_detail_v2, name="application_detail_v2"),
]
