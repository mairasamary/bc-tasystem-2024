from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.urls import reverse

from main.middleware import ProfileWelcomeMiddleware
from main.help_content import HELP_TOPICS
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

    def test_allows_help_during_welcome_step(self):
        """
        Students should be able to access Help even before they complete the
        one-time welcome flow.
        """
        user = CustomUser.objects.create_user(
            email="help_student_welcome@example.com",
            password="password123",
        )
        # profile_welcome_acknowledged defaults to False => welcome step required.
        middleware = ProfileWelcomeMiddleware(lambda request: HttpResponse("ok"))
        rf = RequestFactory()
        request = rf.get("/help/")
        request.user = user

        response = middleware(request)
        self.assertEqual(response.status_code, 200)


class HelpViewAccessTests(TestCase):
    def _create_resume_file(self):
        return SimpleUploadedFile(
            "resume.pdf",
            b"%PDF-1.4 resume",
            content_type="application/pdf",
        )

    def setUp(self):
        self.student = CustomUser.objects.create_user(
            email="help-student@example.com",
            password="password123",
        )
        self.professor = CustomUser.objects.create_user(
            email="help-prof@example.com",
            password="password123",
            professor=True,
        )
        self.admin = CustomUser.objects.create_superuser(
            email="help-admin@example.com",
            password="password123",
        )

    def test_professor_help_home_only_shows_professor_articles(self):
        self.client.force_login(self.professor)

        response = self.client.get(reverse("help_home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Use the professor dashboard and staffing overview")
        self.assertNotContains(response, "Getting started (Welcome + Profile)")
        self.assertNotContains(response, "Use the admin dashboard and system overview")

    def test_admin_help_home_shows_all_audiences(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse("help_home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Getting started (Welcome + Profile)")
        self.assertContains(response, "Use the professor dashboard and staffing overview")
        self.assertContains(response, "Use the admin dashboard and system overview")

    def test_professor_cannot_open_student_article_but_admin_can(self):
        student_topic = next(
            topic for topic in HELP_TOPICS if topic["audience"] == "student"
        )

        self.client.force_login(self.professor)
        professor_response = self.client.get(
            reverse("help_student_topic", kwargs={"topic_id": student_topic["id"]})
        )
        self.assertEqual(professor_response.status_code, 404)

        self.client.force_login(self.admin)
        admin_response = self.client.get(
            reverse("help_student_topic", kwargs={"topic_id": student_topic["id"]})
        )
        self.assertEqual(admin_response.status_code, 200)
        self.assertContains(admin_response, student_topic["title"])

    def test_professor_print_guide_only_shows_professor_articles(self):
        self.client.force_login(self.professor)

        response = self.client.get(reverse("help_print"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TA Connect - Professor Help Guide")
        self.assertContains(response, "Use the professor dashboard and staffing overview")
        self.assertNotContains(response, "Getting started (Welcome + Profile)")
        self.assertNotContains(response, "Use the admin dashboard and system overview")

    def test_admin_print_guide_includes_all_audiences(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse("help_print"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TA Connect - Admin Help Guide")
        self.assertContains(response, "Getting started (Welcome + Profile)")
        self.assertContains(response, "Use the professor dashboard and staffing overview")
        self.assertContains(response, "Use the admin dashboard and system overview")

    def test_allows_help_during_profile_completion_step(self):
        """
        Students should also be able to access Help before their profile is
        fully complete for applying.
        """
        user = CustomUser.objects.create_user(
            email="help_student_profile@example.com",
            password="password123",
        )
        user.eagleid = 12345678
        user.profile_welcome_acknowledged = True
        user.save(update_fields=["eagleid", "profile_welcome_acknowledged"])

        profile = StudentProfile.objects.create(user=user)
        profile.resume.save("resume.pdf", self._create_resume_file(), save=True)
        # graduation_year intentionally missing => profile completion for apply is not done.

        middleware = ProfileWelcomeMiddleware(lambda request: HttpResponse("ok"))
        rf = RequestFactory()
        request = rf.get("/help/")
        request.user = user

        response = middleware(request)
        self.assertEqual(response.status_code, 200)


class HelpSearchRelevanceTests(TestCase):
    def setUp(self):
        self.student = CustomUser.objects.create_user(
            email="help-search-student@example.com",
            password="password123",
        )

    def test_help_search_matches_out_of_order_terms(self):
        """
        Previously the help search required an almost-exact substring match.
        Queries like "resume upload" should still find the Getting started article
        even though the article text uses "upload your resume".
        """
        self.client.force_login(self.student)
        response = self.client.get(reverse("help_students_search"), {"q": "resume upload"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Getting started (Welcome + Profile)")

    def test_help_search_prefers_title_matches(self):
        """
        Title hits should rank strongly so obvious matches show up near the top.
        """
        self.client.force_login(self.student)
        response = self.client.get(reverse("help_students_search"), {"q": "Getting started"})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        # The Getting started card should appear before other student topics.
        first_idx = content.find("Getting started (Welcome + Profile)")
        self.assertNotEqual(first_idx, -1)
        apply_idx = content.find("Apply to a course (TA position)")
        self.assertNotEqual(apply_idx, -1)
        self.assertLess(first_idx, apply_idx)
