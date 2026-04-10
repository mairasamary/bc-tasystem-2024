from django.db import models
from users.models import CustomUser as User
from courses.models import Course
from enum import Enum
from django.urls import reverse
import uuid


def application_resume_upload_path(instance, filename):
    """Store resume under application_resumes/<application_id>/ so each application has its own snapshot."""
    return f'application_resumes/{instance.id}/{filename}'


def application_profile_photo_upload_path(instance, filename):
    """Snapshot of profile photo at time of application."""
    return f'application_profile_photos/{instance.id}/{filename}'


class ApplicationStatus(Enum):
    '''
    Enum for the status of an application
    PENDING - The application has been submitted but not yet reviewed
    APPROVED - The application has been accepted by the professor
    REJECTED - The application has been rejected by the professor or the offer has been rejected by the student
    CONFIRMED - The application offer has been confirmed by the student
    WITHDRAWN - Withdrawn by student or system (e.g. accepted another TA offer)
    '''
    PENDING = 1
    ACCEPTED = 2
    REJECTED = 3
    CONFIRMED = 4
    WITHDRAWN = 5


class Application(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    student = models.ForeignKey(
        User, on_delete=models.CASCADE, default=None, related_name='applications')

    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, default=None, related_name='applications')

    additional_information = models.TextField(max_length=500, blank=True)  # Legacy; prefer structured fields below

    # Structured short-answer fields (character limits enforced in form)
    why_this_course = models.CharField(max_length=500, blank=True)
    relevant_experience = models.CharField(max_length=500, blank=True)
    other_notes = models.CharField(max_length=300, blank=True)

    # Snapshot of profile at time of application (for professor review)
    resume = models.FileField(upload_to=application_resume_upload_path, blank=True, null=True)
    profile_photo = models.FileField(
        upload_to=application_profile_photo_upload_path, blank=True, null=True
    )
    skills_snapshot = models.JSONField(default=list, blank=True)  # [{"name": "Python"}, ...]
    skills_additional_snapshot = models.CharField(
        max_length=500,
        blank=True,
        help_text="Free-text skills from profile at time of application.",
    )
    courses_snapshot = models.JSONField(default=list, blank=True)  # [{"course_name": "..."}]

    status = models.IntegerField(choices=[(
        tag.value, tag.name) for tag in ApplicationStatus], default=ApplicationStatus.PENDING.value)
    withdrawal_reason = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.student.first_name + ' ' + self.student.last_name + ' - ' + self.course.course_title

    def get_absolute_url(self):
        return reverse('applications:application-detail', kwargs={'pk': self.pk})

    def get_status(self):
        return ApplicationStatus(self.status).name

    def reset(self):
        self.status = ApplicationStatus.PENDING.value
        self.save()

    def accept(self):
        self.status = ApplicationStatus.ACCEPTED.value
        self.save()

    def reject(self, feedback=""):
        self.status = ApplicationStatus.REJECTED.value
        # Feedback is optional; only set when provided by professor/admin.
        if hasattr(self, "rejection_feedback"):
            self.rejection_feedback = feedback or ""
        self.save()

    def confirm(self):
        self.status = ApplicationStatus.CONFIRMED.value
        self.save()

    def withdraw(self, reason=""):
        self.status = ApplicationStatus.WITHDRAWN.value
        self.withdrawal_reason = reason
        self.save()
