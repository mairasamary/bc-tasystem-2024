from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import uuid

# Predefined courses for past courses list
PREDEFINED_COURSES = [
    'Computer Science 1', 'Computer Science 2', 'Data Structures',
    'Computer Organization and Lab', 'Computer Systems', 'Logic & Computation',
    'Randomness & Computation', 'Algorithms',
]
GRADE_CHOICES = [
    ('A', 'A'), ('A-', 'A-'), ('B+', 'B+'), ('B', 'B'), ('B-', 'B-'),
    ('C+', 'C+'), ('C', 'C'), ('C-', 'C-'), ('F', 'F'), ('IP', 'IP (In Progress)'),
]


def resume_upload_path(instance, filename):
    import os
    base, ext = os.path.splitext(filename)
    safe_name = base.replace(' ', '_') + ext
    return f'resumes/{safe_name}'


def cv_upload_path(instance, filename):
    import os
    base, ext = os.path.splitext(filename)
    safe_name = base.replace(' ', '_') + ext
    return f'cv/{safe_name}'


def profile_photo_upload_path(instance, filename):
    import os
    base, ext = os.path.splitext(filename)
    return f'profiles/{instance.user_id}_{base}{ext}'


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(unique=True)
    eagleid = models.PositiveIntegerField(default=0000000)
    professor = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.first_name + ' ' + self.last_name

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_professor(self):
        return self.professor

    @property
    def is_student(self):
        return not self.professor

    def reached_max_applications(self):
        lecture_application_count = self.applications.filter(
            course__class_type='Lecture').count()

        non_lecture_applications = self.applications.exclude(
            course__class_type='Lecture')
        non_lecture_class_names = non_lecture_applications.values_list(
            'course__course', flat=True)
        non_lecture_count = len(set(non_lecture_class_names))

        total_applications = lecture_application_count + non_lecture_count

        return total_applications >= 5

    def already_applied_to_course(self, course):
        return self.applications.filter(course=course).exists()

    def is_ta(self):
        return self.course_working_for.exists()

    @property
    def has_ta_assignment(self):
        """True if the user is assigned as a TA for at least one course (template-friendly)."""
        return self.course_working_for.exists()


class Skill(models.Model):
    """Predefined skill that students can add to their profile."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=80, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class StudentProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    profile_photo = models.FileField(upload_to=profile_photo_upload_path, blank=True, null=True)
    resume = models.FileField(upload_to=resume_upload_path, blank=True, null=True)
    cv = models.FileField(upload_to=cv_upload_path, blank=True, null=True)
    graduation_year = models.PositiveIntegerField(blank=True, null=True)
    skills = models.ManyToManyField(Skill, related_name='profiles', blank=True)

    # Self-reported student employment onboarding (TA / on-campus hire)
    onboarding_done_required_form = models.BooleanField(
        default=False,
        verbose_name="Required Onboarding Form for New Student Employees",
    )
    onboarding_done_i9 = models.BooleanField(default=False, verbose_name="Form I-9")
    onboarding_done_payroll_statement = models.BooleanField(
        default=False,
        verbose_name="Payroll Form Statement (Student Hours at Boston College)",
    )
    onboarding_done_w4 = models.BooleanField(default=False, verbose_name="W-4 (Federal Withholding Form)")
    onboarding_done_m4 = models.BooleanField(
        default=False,
        verbose_name="M-4 (Massachusetts Withholding Form)",
    )
    onboarding_done_direct_deposit = models.BooleanField(
        default=False,
        verbose_name="Direct Deposit Enrollment Instructions",
    )

    def __str__(self):
        return f"Profile for {self.user.get_full_name()}"


class PastCourse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='past_courses')
    course_name = models.CharField(max_length=200)
    grade = models.CharField(max_length=4, choices=GRADE_CHOICES)

    class Meta:
        ordering = ['course_name']

    def __str__(self):
        return f"{self.course_name} ({self.grade})"
