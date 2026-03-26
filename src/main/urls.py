from django.urls import path, include
from . import views
from users.views import StudentProfileView

urlpatterns = [
    path("dashboard/", views.admin_dashboard_v2, name="dashboard"),
    path("profile/", StudentProfileView.as_view(), name="student_profile"),
    path("applications/", views.applications_list_v2, name="applications"),
    path("offers/", views.offers_list_v2, name="offers"),
    path("courses/", views.courses_list_v2, name="courses"),
    path("courses/create/", views.create_course_v2, name="create_course"),
    path("courses/<uuid:course_id>/", views.course_overview_v2, name="course_overview"),
    path("courses/<uuid:course_id>/edit/", views.edit_course_v2, name="edit_course"),
    path("courses/<uuid:course_id>/remove-ta/<uuid:user_id>/", views.remove_ta_v2, name="remove_ta"),
    path("courses/upload/", views.upload_courses_v2, name="upload_courses"),
    path("courses/export/", views.export_schedule, name="export_schedule"),
    path("courses/close/", views.close_semester_v2, name="close_semester"),
    path("apply/<uuid:course_id>/", views.apply_to_course_v2, name="apply_to_course"),
    path("make-offer/<uuid:application_id>/", views.make_offer_v2, name="make_offer"),
    path("reject-application/<uuid:application_id>/", views.reject_application_v2, name="reject_application"),
    path("application/<uuid:application_id>/withdraw/", views.withdraw_application_v2, name="withdraw_application"),
    path("application/<uuid:application_id>/edit/", views.edit_application_v2, name="edit_application"),
    path("accept-offer/<uuid:offer_id>/", views.accept_offer_v2, name="accept_offer"),
    path("decline-offer/<uuid:offer_id>/", views.decline_offer_v2, name="decline_offer"),
    path("application/<uuid:application_id>/", views.application_detail_v2, name="application_detail"),
    path("application/<uuid:application_id>/resume/", views.serve_application_resume, name="serve_application_resume"),
    path("evaluations/", include("evaluations.urls")),
]
