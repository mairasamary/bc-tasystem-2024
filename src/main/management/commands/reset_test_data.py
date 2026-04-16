"""
Wipe the database and load a minimal TA test scenario.

Professor + admin + 2 students + 1 course (num_tas=1). One student is
wangedi@bc.edu for Google OAuth.
"""

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management import call_command
from django.core.management.base import BaseCommand

from courses.models import Course
from users.models import CustomUser, Skill, StudentProfile

SKILL_NAMES = [
    "Python",
    "Java",
    "C",
    "C++",
    "JavaScript",
    "MATLAB",
    "R",
    "LaTeX",
    "Git",
    "Debugging",
    "SQL",
    "HTML/CSS",
    "Linux/Unix",
    "Data Structures",
    "Algorithms",
    "Object-Oriented Programming",
    "Tutoring",
    "Office Hours",
    "Grading",
    "Technical Writing",
]


class Command(BaseCommand):
    help = "Flush all data and create an admin, professor, two students, skills, site, and one course (1 TA slot)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-input",
            action="store_true",
            help="Do not prompt for confirmation (same as Django flush --no-input).",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Flushing all database tables..."))
        call_command("flush", interactive=not options["no_input"], verbosity=1)

        # django.contrib.sites expects SITE_ID to exist
        domain = getattr(settings, "SITE_HOSTNAME", "127.0.0.1:8000")
        Site.objects.update_or_create(
            pk=settings.SITE_ID,
            defaults={"domain": domain, "name": "TA Connect"},
        )

        for name in SKILL_NAMES:
            Skill.objects.get_or_create(name=name)

        prof = CustomUser.objects.create_user(
            email="prof.ta@test.bc.edu",
            password="TestProf123!",
            first_name="Pat",
            last_name="Professor",
            professor=True,
            eagleid=100001,
        )

        CustomUser.objects.create_superuser(
            email="admin.help@test.bc.edu",
            password="TestAdmin123!",
            first_name="Avery",
            last_name="Admin",
            eagleid=100000,
        )

        student_oauth = CustomUser(
            email="wangedi@bc.edu",
            first_name="Test",
            last_name="Wang",
            professor=False,
            eagleid=100002,
        )
        student_oauth.set_unusable_password()
        student_oauth.save()

        student_b = CustomUser.objects.create_user(
            email="student2.ta@test.bc.edu",
            password="TestStudent123!",
            first_name="Alex",
            last_name="Student",
            professor=False,
            eagleid=100003,
        )

        StudentProfile.objects.get_or_create(user=student_oauth)
        StudentProfile.objects.get_or_create(user=student_b)

        Course.objects.create(
            term="Spring 2026",
            class_type="Lecture",
            course="CSCI 1101",
            section="01",
            course_title="Computer Science I (Test)",
            instructor_first_name="Pat",
            instructor_last_name="Professor",
            room_name="Higgins 310",
            timeslot="MWF 10:00–10:50",
            max_enroll=100,
            room_size=50,
            num_tas=1,
            description="Seeded test course with one TA slot.",
            status=True,
            is_active=True,
            professor=prof,
        )

        self.stdout.write(self.style.SUCCESS("Done. Test accounts:\n"))
        self.stdout.write(
            "  Admin (password login):     admin.help@test.bc.edu  /  TestAdmin123!\n"
            "  Professor (password login): prof.ta@test.bc.edu  /  TestProf123!\n"
            "  Student (Google OAuth):     wangedi@bc.edu\n"
            "  Student (password login):   student2.ta@test.bc.edu  /  TestStudent123!\n"
            "\n"
            "Course: CSCI 1101 — Computer Science I (Test), Spring 2026, num_tas=1.\n"
            "Upload resumes on each student profile before applying, if your flow requires it.\n"
        )
