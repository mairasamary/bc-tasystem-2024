from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.urls import reverse

from main.middleware import ProfileWelcomeMiddleware
from users.models import CustomUser, StudentProfile

class ProfileWelcomeMiddlewareTests(TestCase):
    def _create_resume_file(self):
        return SimpleUploadedFile(
            "resume.pdf",
            b"%PDF-1.4 resume",
            content_type="application/pdf",
        )

    def test_redirects_to_student_profile_until_grad_year_and_resume_are_complete(self):
        user = CustomUser.objects.create_user(
            email="student3@example.com",
            password="password123",
        )
        user.eagleid = 12345678
        user.profile_welcome_acknowledged = True
        user.save(update_fields=["eagleid", "profile_welcome_acknowledged"])

        profile = StudentProfile.objects.create(user=user)
        profile.resume.save("resume.pdf", self._create_resume_file(), save=True)
        # graduation_year intentionally missing

        middleware = ProfileWelcomeMiddleware(lambda request: HttpResponse("ok"))
        rf = RequestFactory()
        request = rf.get("/courses/")
        request.user = user

        response = middleware(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("student_profile"))

        # Once grad year is set, navigation is allowed.
        profile.graduation_year = 2027
        profile.save(update_fields=["graduation_year"])
        response2 = middleware(request)
        self.assertEqual(response2.status_code, 200)
