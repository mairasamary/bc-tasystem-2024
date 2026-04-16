"""
Capture one help-guide screenshot per Help workflow and save them into:
  src/static/images/help/<topic_id>.png

This automates student, professor, and admin article screenshots so the Help
guides and printable guides can render real in-app examples.
"""

from __future__ import annotations

import concurrent.futures
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import requests


def _setup_django() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    src_dir = repo_root / "src"
    sys.path.insert(0, str(src_dir))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bcta.settings")
    import django

    django.setup()


def _start_server(port: int) -> subprocess.Popen:
    repo_root = Path(__file__).resolve().parent.parent
    manage_py = repo_root / "src" / "manage.py"

    env = os.environ.copy()
    env.setdefault("DJANGO_SETTINGS_MODULE", "bcta.settings")

    proc = subprocess.Popen(
        [
            sys.executable,
            str(manage_py),
            "runserver",
            f"127.0.0.1:{port}",
            "--noreload",
        ],
        cwd=str(repo_root),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    return proc


def _wait_for_server(port: int, timeout_s: int = 60) -> None:
    start = time.time()
    url = f"http://127.0.0.1:{port}/"
    last_err = None
    while time.time() - start < timeout_s:
        try:
            r = requests.get(url, timeout=2)
            if r.status_code < 500:
                return
        except Exception as e:  # noqa: BLE001
            last_err = e
        time.sleep(0.8)
    raise RuntimeError(f"Server did not start in time. Last error: {last_err}")


def _capture(page, url: str, out_path: Path) -> None:
    page.set_viewport_size({"width": 1280, "height": 720})
    page.goto(url, wait_until="networkidle")
    # Ensure the layout settles (Tailwind/CDN may still be rendering).
    page.wait_for_timeout(1200)
    page.screenshot(path=str(out_path), full_page=False)


def main() -> None:
    _setup_django()

    from django.core.files.uploadedfile import SimpleUploadedFile
    from django.core.management import call_command
    from django.urls import reverse

    from applications.models import Application, ApplicationStatus
    from courses.models import Course, CourseQuestion
    from offers.models import Offer, OfferStatus
    from evaluations.models import TAEvaluation
    from users.models import CustomUser, StudentProfile

    from playwright.sync_api import sync_playwright

    repo_root = Path(__file__).resolve().parent.parent
    out_dir = repo_root / "src" / "static" / "images" / "help"
    out_dir.mkdir(parents=True, exist_ok=True)

    # --- Reset + seed DB ---
    call_command("migrate", interactive=False, verbosity=0)
    call_command("reset_test_data", no_input=True, verbosity=0)

    professor = CustomUser.objects.get(email="prof.ta@test.bc.edu")
    student = CustomUser.objects.get(email="student2.ta@test.bc.edu")
    profile = StudentProfile.objects.get(user=student)
    course = Course.objects.first()
    if course is None:
        raise RuntimeError("No course found after reset_test_data.")

    admin = CustomUser.objects.create_superuser(
        email="admin.help@test.bc.edu",
        password="TestAdmin123!",
        first_name="Avery",
        last_name="Admin",
    )

    # Ensure we start with an incomplete profile for the "Getting started" screenshot.
    student.profile_welcome_acknowledged = False
    student.eagleid = 0
    student.save(update_fields=["profile_welcome_acknowledged", "eagleid"])
    profile.graduation_year = None
    if profile.resume:
        profile.resume.delete(save=True)
    profile.save(update_fields=["graduation_year", "resume"])

    student_id = student.id
    course_id = course.id
    professor_id = professor.id

    # --- Start server for browser capture ---
    port = 8001
    proc = _start_server(port)
    try:
        _wait_for_server(port)

        base_url = f"http://127.0.0.1:{port}"

        with sync_playwright() as p:
            # Use Firefox to avoid any missing Chromium executable issues.
            browser = p.firefox.launch()
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

            def _login(email: str, password: str):
                context = browser.new_context(viewport={"width": 1280, "height": 720})
                page = context.new_page()
                login_url = f"{base_url}/users/login/"
                page.goto(login_url, wait_until="networkidle")

                username_field = page.locator('form input[name="username"]')
                if username_field.count() == 0:
                    text_inputs = page.locator(
                        "form input[type='text'], form input[type='email']"
                    ).all()
                    if not text_inputs:
                        raise RuntimeError("Could not locate username input on login page.")
                    text_inputs[0].fill(email)
                else:
                    username_field.first.fill(email)

                page.locator("form input[type='password']").first.fill(password)
                page.locator("form button[type='submit']").first.click()
                page.wait_for_timeout(1500)
                return context, page

            def _make_profile_complete() -> None:
                s = CustomUser.objects.get(id=student_id)
                p = StudentProfile.objects.get(user=s)
                s.profile_welcome_acknowledged = True
                s.eagleid = 12345678
                s.save(update_fields=["profile_welcome_acknowledged", "eagleid"])

                p.graduation_year = 2027
                if p.resume:
                    p.resume.delete(save=True)
                resume_file = SimpleUploadedFile(
                    "resume.pdf",
                    b"%PDF-1.4 TA Connect dummy resume",
                    content_type="application/pdf",
                )
                p.resume.save(resume_file.name, resume_file, save=True)
                p.save(update_fields=["graduation_year"])

            def _create_pending_application_and_question() -> str:
                s = CustomUser.objects.get(id=student_id)
                c = Course.objects.get(id=course_id)
                CourseQuestion.objects.get_or_create(
                    course=c,
                    question_text="What grade did you earn in this course?",
                    defaults={"is_required": True, "order": 1},
                )
                app = Application.objects.create(
                    student=s,
                    course=c,
                    status=ApplicationStatus.PENDING.value,
                    why_this_course="I enjoy helping students build programming fundamentals.",
                    relevant_experience="Prior tutoring and office hours support.",
                    other_notes="Available for recitation and grading support.",
                    additional_information="Interested in leading review sessions.",
                )
                return str(app.id)

            def _create_pending_offer(app_id_str: str) -> None:
                s = CustomUser.objects.get(id=student_id)
                c = Course.objects.get(id=course_id)
                app = Application.objects.get(id=app_id_str)
                Offer.objects.get_or_create(
                    application=app,
                    course=c,
                    recipient=s,
                    sender=CustomUser.objects.get(id=professor_id),
                    defaults={"status": OfferStatus.PENDING.value},
                )

            def _assign_ta_and_create_evaluation() -> None:
                c = Course.objects.get(id=course_id)
                s = CustomUser.objects.get(id=student_id)
                prof = CustomUser.objects.get(id=professor_id)
                c.current_tas.add(s)
                TAEvaluation.objects.get_or_create(
                    reviewer=prof,
                    ta=s,
                    course=c,
                    defaults={
                        "rating_punctuality": 5,
                        "rating_communication": 4,
                        "rating_technical": 5,
                        "rating_professionalism": 5,
                        "rating_overall": 5,
                        "feedback": "Strong technical TA with reliable communication.",
                    },
                )

            # --- 1) Getting started: /profile/ with incomplete profile ---
            student_context, student_page = _login(
                "student2.ta@test.bc.edu",
                "TestStudent123!",
            )
            getting_started_url = f"{base_url}/profile/"
            _capture(student_page, getting_started_url, out_dir / "getting-started.png")

            # --- 2) Apply to a course: /apply/<course_id>/ with complete profile ---
            executor.submit(_make_profile_complete).result()

            apply_url = f"{base_url}{reverse('apply_to_course', kwargs={'course_id': course.id})}"
            _capture(student_page, apply_url, out_dir / "apply-to-course.png")

            # --- 3) Edit / withdraw application: create PENDING application + screenshot detail ---
            app_id_str = executor.submit(_create_pending_application_and_question).result()
            app_id = app_id_str  # string UUID is fine for Django/URL in this context
            app_url = f"{base_url}{reverse('application_detail', kwargs={'application_id': app_id})}"
            _capture(student_page, app_url, out_dir / "edit-withdraw-application.png")

            # --- Professor captures with seeded application data ---
            professor_context, professor_page = _login(
                "prof.ta@test.bc.edu",
                "TestProf123!",
            )
            _capture(
                professor_page,
                f"{base_url}/dashboard/",
                out_dir / "professor-dashboard-and-staffing.png",
            )
            _capture(
                professor_page,
                app_url,
                out_dir / "review-applications-and-send-offers.png",
            )
            course_url = f"{base_url}{reverse('course_overview', kwargs={'course_id': course.id})}"
            _capture(
                professor_page,
                course_url,
                out_dir / "manage-course-details-and-questions.png",
            )

            # --- 4) Respond to TA offers: create PENDING offer + screenshot /offers/ ---
            executor.submit(_create_pending_offer, app_id_str).result()
            offers_url = f"{base_url}/offers/"
            _capture(student_page, offers_url, out_dir / "respond-to-offers.png")

            # --- 5) Employment onboarding: assign TA role + screenshot checklist ---
            executor.submit(_assign_ta_and_create_evaluation).result()

            onboarding_url = f"{base_url}/employment-onboarding/"
            _capture(student_page, onboarding_url, out_dir / "employment-onboarding.png")

            _capture(
                professor_page,
                f"{base_url}{reverse('evaluations:list')}",
                out_dir / "track-offers-and-ta-evaluations.png",
            )

            # --- Admin captures ---
            admin_context, admin_page = _login(
                "admin.help@test.bc.edu",
                "TestAdmin123!",
            )
            _capture(
                admin_page,
                f"{base_url}/dashboard/",
                out_dir / "admin-dashboard-and-system-overview.png",
            )
            _capture(
                admin_page,
                f"{base_url}/courses/",
                out_dir / "create-edit-and-upload-courses.png",
            )
            _capture(
                admin_page,
                f"{base_url}/onboarding-status/",
                out_dir / "manage-onboarding-status-and-reminders.png",
            )
            _capture(
                admin_page,
                f"{base_url}/courses/upload/",
                out_dir / "export-schedule-and-close-semester.png",
            )

            student_context.close()
            professor_context.close()
            admin_context.close()
            browser.close()
            executor.shutdown(wait=True)

    finally:
        # Ensure the server is stopped.
        proc.send_signal(signal.SIGTERM)
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()

    print("Captured help screenshots into:")
    for p in sorted(out_dir.glob("*.png")):
        print(" -", p)


if __name__ == "__main__":
    main()

