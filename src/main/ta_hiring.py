from django.urls import reverse

from applications.models import Application, ApplicationStatus
from main.constants import BC_STUDENT_EMPLOYMENT_NEW_HIRES_URL
from main.notifications import create_notification
from main.utils import app_site_absolute_url, send_notification_email

CS_TA_GUIDELINES_CONTRACT_URL = (
    "https://docs.google.com/forms/d/e/1FAIpQLSfcb4M_9cD8CW_nz8eQrhEKiinBjpobpTMkTHe-TTBDODv4iQ/viewform"
)
PEOPLESOFT_PAYROLL_COMPENSATION_URL = (
    "https://sites.google.com/bc.edu/human-resources/peoplesoft-hr/peoplesoft-hr-employee-self-service/employee-self-service-payroll-compensation"
)
DIRECT_DEPOSIT_INSTRUCTIONS_URL = (
    "https://www.bc.edu/content/dam/files/offices/hr/pdf/Direct%20Deposit%20Instructions.pdf"
)


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
        "Once you accept a TA offer in the Computer Science department, please complete the onboarding items below.",
        "",
        "1) Review and sign the CS Teaching Assistant Guidelines Contract 2026-2027 Google Form:",
        CS_TA_GUIDELINES_CONTRACT_URL,
        "",
        "2) If you are a new hire and need to complete an I-9, submit your I-9 paperwork in person at "
        "the Student Employment office in Lyons and bring original documents:",
        BC_STUDENT_EMPLOYMENT_NEW_HIRES_URL,
        "",
        "3) If you are a new-hire international student who needs a Social Security number, follow the "
        "international student instructions here:",
        BC_STUDENT_EMPLOYMENT_NEW_HIRES_URL + "#tab-international_f_1_students",
        "",
        "If your paperwork is complete, your timecard appears in Employee Time Reporting near the beginning "
        "of the employment period. If you are a new hire, complete paperwork as soon as you are on campus.",
        "",
        "If you have worked on campus previously and already have an I-9 on file, only Step 1 is required.",
        "",
        "You will know you are in the system when your timecard appears in Kronos:",
        "Agora Portal >> Account and Personal Info >> Employee Time Reporting (select your student role).",
        "",
        "Only after that can you add or update direct deposit and tax documents in PeopleSoft HR:",
        "Agora Portal >> Human Resources >> PeopleSoft Human Resources Services.",
        "Tax withholding certificates (W-4 Federal and M-4 MA):",
        PEOPLESOFT_PAYROLL_COMPENSATION_URL,
        "Direct deposit setup instructions:",
        DIRECT_DEPOSIT_INSTRUCTIONS_URL,
        "",
        "Important: Hourly-paid student employees must enter their hours in Kronos by the end of each week "
        "(Friday) to be paid on time.",
        "",
        "If a step is not applicable to you (for example, international-only steps), check it off and disregard in the checklist.",
        "If you run into any issues, please do not hesitate to reach out to Mary Mulkeen (mary.mulkeen@bc.edu).",
        "",
        "Use your TA Connect onboarding checklist to track these steps:",
        checklist_url,
    ]
    send_notification_email(
        subject=f"TA Employment Onboarding Next Steps ({course_code})",
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
                    "You may browse other open courses on TA Connect.",
                ],
            )
