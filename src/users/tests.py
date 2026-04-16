from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from .forms import StudentProfileForm
from .models import CustomUser, StudentProfile

class StudentProfileCompletionTests(TestCase):
    def _create_resume_file(self):
        return SimpleUploadedFile(
            "resume.pdf",
            b"%PDF-1.4 resume",
            content_type="application/pdf",
        )

    def test_has_complete_profile_for_apply_requires_graduation_year(self):
        user = CustomUser.objects.create_user(
            email="student@example.com",
            password="password123",
        )
        user.eagleid = 12345678
        user.profile_welcome_acknowledged = True
        user.save(update_fields=["eagleid", "profile_welcome_acknowledged"])

        profile = StudentProfile.objects.create(user=user)
        profile.resume.save("resume.pdf", self._create_resume_file(), save=True)

        # Grad year missing => incomplete
        self.assertFalse(user.has_complete_profile_for_apply())

        profile.graduation_year = 2027
        profile.save(update_fields=["graduation_year"])

        # Grad year present => complete
        self.assertTrue(user.has_complete_profile_for_apply())

    def test_has_complete_profile_for_apply_requires_eight_digit_eagleid(self):
        user = CustomUser.objects.create_user(
            email="student_eagleid@example.com",
            password="password123",
        )
        user.profile_welcome_acknowledged = True
        user.save(update_fields=["profile_welcome_acknowledged"])

        profile = StudentProfile.objects.create(user=user)
        profile.resume.save("resume.pdf", self._create_resume_file(), save=True)
        profile.graduation_year = 2027
        profile.save(update_fields=["graduation_year"])

        # Eagle ID too short => incomplete
        user.eagleid = 1234567
        user.save(update_fields=["eagleid"])
        self.assertFalse(user.has_complete_profile_for_apply())

        # Eagle ID exactly 8 digits => complete
        user.eagleid = 12345678
        user.save(update_fields=["eagleid"])
        self.assertTrue(user.has_complete_profile_for_apply())

    def test_student_profile_form_requires_graduation_year_and_resume_when_missing(self):
        user = CustomUser.objects.create_user(
            email="student2@example.com",
            password="password123",
        )
        user.profile_welcome_acknowledged = True
        user.eagleid = 123
        user.save(update_fields=["profile_welcome_acknowledged", "eagleid"])

        profile = StudentProfile.objects.create(user=user)
        form = StudentProfileForm(instance=profile, data={}, files={})
        self.assertFalse(form.is_valid())
        self.assertIn("graduation_year", form.errors)
        self.assertIn("resume", form.errors)
