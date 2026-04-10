from django.urls import reverse

from applications.models import Application, ApplicationStatus
from main.constants import BC_STUDENT_EMPLOYMENT_NEW_HIRES_URL
from main.notifications import create_notification
from main.utils import app_site_absolute_url, send_notification_email


def send_student_ta_acceptance_onboarding_email(user, course_code: str, course_title: str) -> None:
    """Email sent when a student accepts a TA offer (student employment onboarding)."""
    if not getattr(user, "email", None):
        return
    checklist_path = reverse("employment_onboarding")
    checklist_url = app_site_absolute_url(checklist_path)
    name = user.get_full_name() or "Student"
    lines = [
        f"Dear {name},",
        "",
        f"Congratulations! You have accepted your TA assignment for {course_code} — {course_title}.",
        "",
        "All newly hired student employees who will be working for the first time at BC must complete "
        "the following onboarding documents before they begin to work. Note that students must secure "
        "a job on campus or through our Off-Campus Federal Work-Study (FWS) Program to complete these "
        "student employment onboarding forms.",
        "",
        "The Form I-9 Employment Eligibility Verification, Required Onboarding Form for New Student "
        "Employees, and Payroll Form Statement (Student Hours at Boston College) are paper forms and "
        "must be completed in person at the Office of Student Services.",
        "",
        "These three forms are required to satisfy the Form I-9 requirement and must be completed only "
        "once for all student jobs at Boston College. Students are unable to begin working until they "
        "have completed the Form I-9 entirely, and it is on file with Student Employment.",
        "",
        "Please follow the link below for instructions on how to complete each form:",
        BC_STUDENT_EMPLOYMENT_NEW_HIRES_URL,
        "",
        "On TA Buzz you can use your personal onboarding checklist to self-report which forms you have "
        "completed: Required Onboarding Form for Student Employees, Form I-9, Payroll Form Statement, "
        "W-4 (Federal Withholding Form), M-4 (Massachusetts Withholding Form), and Direct Deposit "
        "Enrollment Instructions.",
        checklist_url,
        "",
        "Note that all completed forms should be brought to the Office of Student Services. The link to "
        "find the forms is here:",
        BC_STUDENT_EMPLOYMENT_NEW_HIRES_URL,
    ]
    send_notification_email(
        subject=f"TA assignment confirmed — student employment onboarding ({course_code})",
        recipients=user.email,
        message_lines=lines,
    )


def reject_pending_applications_when_course_filled(course):
    """
    When every TA slot is assigned, reject applicants who never received an offer.
    Students with a pending offer stay ACCEPTED until they respond; they are not PENDING.
    """
    if not course.num_tas or course.current_tas.count() < course.num_tas:
        return
    feedback = "All TA positions for this course have been filled."
    pending = Application.objects.filter(
        course=course,
        status=ApplicationStatus.PENDING.value,
    ).select_related("student")
    for app in pending:
        app.reject(feedback)
        create_notification(
            user=app.student,
            title=f"Your application for {app.course.course} was not selected",
            target_url=reverse("application_detail", kwargs={"application_id": app.id}),
        )
        if app.student.email:
            send_notification_email(
                subject=f"Application Update for {app.course.course}",
                recipients=app.student.email,
                message_lines=[
                    f"Dear {app.student.get_full_name()},",
                    f"Thank you for your interest in TAing for {app.course.course} — {app.course.course_title}.",
                    "All TA positions for this course have been filled.",
                    "You may browse other open courses on TA Buzz.",
                ],
            )
