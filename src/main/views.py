
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Count, F, Q
from courses.models import Course
from applications.models import Application, ApplicationStatus
from applications.forms import ApplicationForm
from offers.models import Offer, OfferStatus
from users.models import StudentProfile, PastCourse

User = get_user_model()

def home(request):
    courses = Course.objects.all()
    context = {'courses': courses}
    return render(request, 'home.html', context)

@login_required
def admin_dashboard_v2(request):
    # Admin: full system overview (stats + recent apps/offers)
    if request.user.is_superuser:
        pending_apps_count = Application.objects.filter(status=ApplicationStatus.PENDING.value).count()
        total_offers_count = Offer.objects.count()
        active_courses_count = Course.objects.filter(status=True).count()
        total_users_count = User.objects.count()
        pending_apps = Application.objects.filter(status=ApplicationStatus.PENDING.value).select_related('student', 'course').order_by('-id')[:5]
        recent_offers = Offer.objects.all().select_related('recipient', 'course').order_by('-created_at')[:5]
        context = {
            'pending_apps_count': pending_apps_count,
            'total_offers_count': total_offers_count,
            'active_courses_count': active_courses_count,
            'total_users_count': total_users_count,
            'pending_apps': pending_apps,
            'recent_offers': recent_offers,
        }
        return render(request, 'dashboard_v2.html', context)

    # Professor: 4 stat cards + Course Staffing Overview table
    if request.user.is_professor:
        my_active_courses_count = Course.objects.filter(
            professor=request.user, status=True
        ).count()
        understaffed_count = (
            Course.objects.filter(professor=request.user, status=True)
            .annotate(tas_count=Count('current_tas', distinct=True))
            .filter(tas_count__lt=F('num_tas'))
            .count()
        )
        pending_applications_count = Application.objects.filter(
            course__professor=request.user,
            status=ApplicationStatus.PENDING.value,
        ).count()
        pending_offers_count = Offer.objects.filter(
            sender=request.user, status=OfferStatus.PENDING.value
        ).count()
        staffing_overview = (
            Course.objects.filter(professor=request.user)
            .annotate(
                tas_count=Count('current_tas', distinct=True),
                pending_apps_count=Count(
                    'applications',
                    filter=Q(applications__status=ApplicationStatus.PENDING.value),
                    distinct=True,
                ),
                pending_offers_count=Count(
                    'offer_course',
                    filter=Q(
                        offer_course__status=OfferStatus.PENDING.value,
                        offer_course__sender=request.user,
                    ),
                    distinct=True,
                ),
            )
            .order_by('-term', 'course')
        )
        context = {
            'my_active_courses_count': my_active_courses_count,
            'understaffed_count': understaffed_count,
            'pending_applications_count': pending_applications_count,
            'pending_offers_count': pending_offers_count,
            'staffing_overview': staffing_overview,
        }
        return render(request, 'professor_dashboard.html', context)

    # Student Dashboard: stats for minimal, action-oriented UI
    my_apps = Application.objects.filter(student=request.user).select_related('course').order_by('-id')
    my_offers = Offer.objects.filter(recipient=request.user).select_related('course', 'sender').order_by('-created_at')
    assigned_course = request.user.course_working_for.first()
    current_term = (assigned_course.term or "").strip() if assigned_course else ""
    if not current_term:
        t = Course.objects.order_by('-term').values_list('term', flat=True).first()
        current_term = (t or "").strip()
    counted_statuses = [
        ApplicationStatus.PENDING.value,
        ApplicationStatus.ACCEPTED.value,
        ApplicationStatus.CONFIRMED.value,
    ]
    applications_active_this_term = (
        Application.objects.filter(
            student=request.user,
            course__term__iexact=current_term,
            status__in=counted_statuses,
        ).count()
        if current_term
        else 0
    )
    offers_awaiting_response = Offer.objects.filter(
        recipient=request.user, status=OfferStatus.PENDING.value
    ).count()
    has_accepted_offer_this_term = Offer.objects.filter(
        recipient=request.user, status=OfferStatus.ACCEPTED.value
    ).exists()
    assigned_course_name = assigned_course.course if assigned_course else None
    context = {
        'my_apps': my_apps,
        'my_offers': my_offers,
        'applications_active_this_term': applications_active_this_term,
        'offers_awaiting_response': offers_awaiting_response,
        'has_accepted_offer_this_term': has_accepted_offer_this_term,
        'assigned_course_name': assigned_course_name,
    }
    return render(request, 'student_dashboard.html', context)

@login_required
def applications_list_v2(request):
    # Professors see only applications for their courses (even if also superuser)
    if request.user.is_professor:
        apps = Application.objects.filter(course__professor=request.user).select_related('student', 'course').order_by('-id')
    elif request.user.is_superuser:
        apps = Application.objects.select_related('student', 'course').order_by('-id')
    else:
        apps = Application.objects.filter(student=request.user).select_related('student', 'course').order_by('-id')
    return render(request, 'applications_v2.html', {'apps': apps})

@login_required
def offers_list_v2(request):
    # Professors see only offers they sent (even if also superuser)
    if request.user.is_professor:
        offers = Offer.objects.filter(sender=request.user).select_related('recipient', 'course').order_by('-created_at')
    elif request.user.is_superuser:
        offers = Offer.objects.select_related('recipient', 'course', 'sender').order_by('-created_at')
    else:
        offers = Offer.objects.filter(recipient=request.user).select_related('recipient', 'course').order_by('-created_at')
    return render(request, 'offers_v2.html', {'offers': offers})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, FileResponse
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from applications.models import Application, ApplicationStatus
from courses.forms import CourseForm
from courses.views import UploadView

PER_PAGE_CHOICES = [10, 20, 50]

@login_required
def courses_list_v2(request):
    query = request.GET.get('q')
    professor_id = request.GET.get('professor')
    status_filter = request.GET.get('status', '')
    class_type_filter = request.GET.get('class_type', '')
    course_level = request.GET.get('course_level', '')
    per_page_param = request.GET.get('per_page', '10')
    courses = Course.objects.all().order_by('course')

    if query:
        courses = courses.filter(
            Q(course__icontains=query) |
            Q(course_title__icontains=query) |
            Q(instructor_first_name__icontains=query) |
            Q(instructor_last_name__icontains=query)
        )
    if professor_id:
        courses = courses.filter(professor_id=professor_id)
    if status_filter == 'active':
        courses = courses.filter(status=True)
    elif status_filter == 'closed':
        courses = courses.filter(status=False)
    if class_type_filter:
        courses = courses.filter(class_type=class_type_filter)
    if course_level and course_level in ('1', '2', '3', '4', '5'):
        courses = courses.filter(course__iregex=r'^\D*' + course_level + r'\d{3}')

    if per_page_param == 'all':
        per_page_size = 9999
        per_page = 'all'
    else:
        try:
            n = int(per_page_param)
            per_page_size = n if n in PER_PAGE_CHOICES else 10
            per_page = str(per_page_size)
        except (ValueError, TypeError):
            per_page_size = 10
            per_page = '10'

    paginator = Paginator(courses, per_page_size)
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)
    courses = page.object_list

    professors = User.objects.filter(professor=True).order_by('last_name', 'first_name')

    if not request.user.is_professor:
        applied_course_ids = Application.objects.filter(student=request.user).values_list('course_id', flat=True)
        # For disabling Apply entrypoints: limit 5 per term or already assigned this term
        assigned_course = request.user.course_working_for.first()
        current_term = (assigned_course.term or "").strip() if assigned_course else ""
        if not current_term:
            t = Course.objects.order_by('-term').values_list('term', flat=True).first()
            current_term = (t or "").strip()
        counted = [
            ApplicationStatus.PENDING.value,
            ApplicationStatus.ACCEPTED.value,
            ApplicationStatus.CONFIRMED.value,
        ]
        apps_this_term = (
            Application.objects.filter(
                student=request.user,
                course__term__iexact=current_term,
                status__in=counted,
            ).count()
            if current_term
            else 0
        )
        has_accepted = Offer.objects.filter(
            recipient=request.user, status=OfferStatus.ACCEPTED.value
        ).exists()
        student_can_apply = not (apps_this_term >= 5 or has_accepted)
    else:
        applied_course_ids = []
        student_can_apply = True  # professors don't use Apply

    get_copy = request.GET.copy()
    if 'page' in get_copy:
        del get_copy['page']
    query_string = get_copy.urlencode()

    return render(request, 'courses_v2.html', {
        'courses': courses,
        'applied_course_ids': applied_course_ids,
        'professors': professors,
        'page': page,
        'paginator': paginator,
        'query_string': query_string,
        'per_page': per_page,
        'student_can_apply': student_can_apply,
    })

@login_required
def create_course_v2(request):
    if not request.user.is_superuser:
        messages.error(request, "Only admins can create courses.")
        return redirect('courses_v2')

    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            if course.professor:
                course.instructor_first_name = course.professor.first_name
                course.instructor_last_name = course.professor.last_name
            else:
                course.instructor_first_name = ''
                course.instructor_last_name = ''
            course.save()
            messages.success(request, f"Course {course.course} - {course.course_title} created successfully.")
            return redirect('courses_v2')
    else:
        form = CourseForm()

    return render(request, 'create_course_v2.html', {'form': form})


@login_required
def course_overview_v2(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    context = {'course': course}
    if not request.user.is_professor:
        applied_course_ids = list(
            Application.objects.filter(student=request.user).values_list('course_id', flat=True)
        )
        context['applied_course_ids'] = applied_course_ids
        assigned_course = request.user.course_working_for.first()
        current_term = (assigned_course.term or "").strip() if assigned_course else ""
        if not current_term:
            t = Course.objects.order_by('-term').values_list('term', flat=True).first()
            current_term = (t or "").strip()
        counted = [
            ApplicationStatus.PENDING.value,
            ApplicationStatus.ACCEPTED.value,
            ApplicationStatus.CONFIRMED.value,
        ]
        apps_this_term = (
            Application.objects.filter(
                student=request.user,
                course__term__iexact=current_term,
                status__in=counted,
            ).count()
            if current_term
            else 0
        )
        has_accepted = Offer.objects.filter(
            recipient=request.user, status=OfferStatus.ACCEPTED.value
        ).exists()
        context['student_can_apply'] = not (apps_this_term >= 5 or has_accepted)
    else:
        context['applied_course_ids'] = []
        context['student_can_apply'] = False
    return render(request, 'course_overview_v2.html', context)

@login_required
def edit_course_v2(request, course_id):
    if not (request.user.is_superuser or request.user.is_professor):
        messages.error(request, "You don't have permission to edit courses.")
        return redirect('courses_v2')
    course = get_object_or_404(Course, id=course_id)
    if request.user.is_professor and not request.user.is_superuser and course.professor_id != request.user.id:
        messages.error(request, "You can only edit your own courses.")
        return redirect('courses_v2')
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            # Courses only close when full (TA capacity) or admin closes semester; enforce full => closed on edit
            if course.current_tas.count() >= course.num_tas:
                course.status = False
                course.save(update_fields=['status'])
            messages.success(request, f"Course {course.course} - {course.course_title} updated successfully.")
            return redirect('courses_v2')
    else:
        form = CourseForm(instance=course)
    return render(request, 'edit_course_v2.html', {'form': form, 'course': course})


@login_required
def upload_courses_v2(request):
    if not request.user.is_superuser:
        messages.error(request, "Only admins can upload courses.")
        return redirect('courses_v2')

    if request.method == 'POST':
        excel_file = request.FILES.get("excel_file")
        if excel_file:
            upload_view = UploadView()
            upload_view.request = request
            upload_view.process_excel_file(excel_file)
            messages.success(request, "Successfully uploaded courses from Excel file.")
        else:
            messages.error(request, "Please select an Excel file to upload.")
        return redirect('courses_v2')

    return render(request, 'upload_courses_v2.html')

@login_required
def close_semester_v2(request):
    if not request.user.is_superuser:
        messages.error(request, "Only admins can close the semester.")
        return redirect('courses_v2')

    if request.method == 'POST':
        # Close all courses for the semester (the other way courses close; the other is full TA capacity)
        Course.objects.all().update(is_active=False, status=False)
        messages.success(request, "Successfully closed all courses for the semester.")

    return redirect('courses_v2')

# Statuses that count toward the 5-application-per-term limit (Rejected/Withdrawn do not count)
APPLICATION_LIMIT_COUNTED_STATUSES = [
    ApplicationStatus.PENDING.value,
    ApplicationStatus.ACCEPTED.value,
    ApplicationStatus.CONFIRMED.value,
]


@login_required
def apply_to_course_v2(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Closed courses do not accept applications
    if not course.status:
        messages.error(request, "This course is closed and is not accepting applications.")
        return redirect('courses_v2')

    # Permission checks
    if request.user.is_professor:
        messages.error(request, "Professors cannot apply for TA positions.")
        return redirect('courses_v2')

    if hasattr(request.user, 'is_ta') and request.user.is_ta():
        messages.error(request, "You are already a TA for a course.")
        return redirect('courses_v2')

    # Check if already applied to this course
    if Application.objects.filter(student=request.user, course=course).exists():
        messages.warning(request, "You have already applied to this course.")
        return redirect('courses_v2')

    # Require profile with resume before applying
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    if not profile.resume:
        messages.error(request, "Please complete your profile before applying. Upload a resume in your Profile page.")
        return redirect('student_profile_v2')

    def count_applications_for_term(student, term):
        if not term:
            return 0
        norm_term = term.strip()
        return Application.objects.filter(
            student=student,
            course__term__iexact=norm_term,
            status__in=APPLICATION_LIMIT_COUNTED_STATUSES,
        ).count()

    # Enforce 5-application limit per term: block when they already have 5
    current_term_count = count_applications_for_term(request.user, course.term)
    if current_term_count >= 5:
        if request.method == 'POST':
            return HttpResponse(
                "You have reached the 5-course application limit for this term.",
                status=400,
            )
        messages.error(request, "You have reached the 5-course application limit for this term.")
        return redirect('courses_v2')

    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            # Re-check limit right before save
            if count_applications_for_term(request.user, course.term) >= 5:
                return HttpResponse(
                    "You have reached the 5-course application limit for this term.",
                    status=400,
                )
            app = form.save(commit=False)
            app.student = request.user
            app.course = course
            app.status = ApplicationStatus.PENDING.value
            # Snapshot profile at time of application
            app.skills_snapshot = [{"name": s.name} for s in profile.skills.all()]
            app.courses_snapshot = [
                {"course_name": pc.course_name, "grade": pc.grade}
                for pc in request.user.past_courses.all()
            ]
            app.save()
            # Copy resume file to application snapshot (so professor sees what was submitted)
            if profile.resume:
                import os
                app.resume.save(os.path.basename(profile.resume.name), profile.resume, save=True)

            messages.success(request, f"Successfully applied to {course.course}.")
            return redirect('courses_v2')
    else:
        form = ApplicationForm()

    # Profile summary for template (resume link, skills, past courses)
    profile_skills = list(profile.skills.all().order_by('name'))
    profile_past_courses = list(request.user.past_courses.all().order_by('course_name'))
    return render(request, 'application_form_v2.html', {
        'form': form,
        'course': course,
        'profile': profile,
        'profile_skills': profile_skills,
        'profile_past_courses': profile_past_courses,
    })

@login_required
def make_offer_v2(request, application_id):
    if request.method == 'POST':
        if not (request.user.is_professor or request.user.is_superuser):
            messages.error(request, "Only professors or admins can make offers.")
            return redirect('applications_v2')
            
        app = get_object_or_404(Application, id=application_id)
        
        # Create Offer
        Offer.objects.create(
            recipient=app.student,
            course=app.course,
            sender=request.user,
            application=app,
            status=OfferStatus.PENDING.value
        )
        
        # Update Application status
        app.status = ApplicationStatus.ACCEPTED.value
        app.save()
        
        messages.success(request, f"Offer sent to {app.student.get_full_name()} for {app.course.course}.")
        
    return redirect('applications_v2')

@login_required
def reject_application_v2(request, application_id):
    if request.method == 'POST':
        if not (request.user.is_professor or request.user.is_superuser):
            messages.error(request, "Only professors or admins can reject applications.")
            return redirect('applications_v2')
            
        app = get_object_or_404(Application, id=application_id)
        
        # Use model method
        app.reject()
        
        messages.success(request, f"Application for {app.student.get_full_name()} has been rejected.")
        
    return redirect('applications_v2')

@login_required
def withdraw_application_v2(request, application_id):
    if request.method != 'POST':
        return redirect('application_detail_v2', application_id=application_id)
    app = get_object_or_404(Application, id=application_id)
    if request.user != app.student:
        messages.error(request, "You are not authorized to withdraw this application.")
        return redirect('applications_v2')
    if app.status not in (ApplicationStatus.PENDING.value, ApplicationStatus.ACCEPTED.value):
        messages.error(request, "Only pending or accepted applications can be withdrawn.")
        return redirect('applications_v2')
    app.withdraw("Withdrawn by student")
    messages.success(request, "Your application has been withdrawn.")
    return redirect('applications_v2')


@login_required
def edit_application_v2(request, application_id):
    """Allow students to edit their own application (additional_information) when PENDING or ACCEPTED."""
    app = get_object_or_404(Application, id=application_id)
    if request.user != app.student:
        messages.error(request, "You are not authorized to edit this application.")
        return redirect('applications_v2')
    if app.status not in (ApplicationStatus.PENDING.value, ApplicationStatus.ACCEPTED.value):
        messages.error(request, "Only pending or accepted applications can be edited.")
        return redirect('application_detail_v2', application_id=app.id)

    course = app.course
    if request.method == 'POST':
        form = ApplicationForm(request.POST, instance=app)
        if form.is_valid():
            form.save()
            messages.success(request, "Your application has been updated.")
            return redirect('application_detail_v2', application_id=app.id)
    else:
        form = ApplicationForm(instance=app)

    return render(request, 'application_form_v2.html', {
        'form': form,
        'course': course,
        'application': app,
        'is_edit': True,
    })


@login_required
def accept_offer_v2(request, offer_id):
    if request.method == 'POST':
        offer = get_object_or_404(Offer, id=offer_id)
        if request.user != offer.recipient:
            messages.error(request, "You are not authorized to accept this offer.")
            return redirect('offers_v2')
        # Enforce 1 TA position per term: block if student already has an accepted offer for this term
        term = (offer.course.term or "").strip()
        if term:
            has_other_accepted = Offer.objects.filter(
                recipient=offer.recipient,
                course__term__iexact=term,
                status=OfferStatus.ACCEPTED.value,
            ).exclude(id=offer.id).exists()
            if has_other_accepted:
                messages.error(request, "You can only accept 1 TA position per term.")
                return redirect('offers_v2')
        with transaction.atomic():
            offer.accept()
            if term:
                # Withdraw other same-term applications (active: PENDING or ACCEPTED)
                Application.objects.filter(
                    student=offer.recipient,
                    course__term__iexact=term,
                ).exclude(id=offer.application_id).filter(
                    status__in=[ApplicationStatus.PENDING.value, ApplicationStatus.ACCEPTED.value],
                ).update(
                    status=ApplicationStatus.WITHDRAWN.value,
                    withdrawal_reason="Accepted another TA offer",
                )
                # Close other same-term pending offers (status only; applications already withdrawn)
                Offer.objects.filter(
                    recipient=offer.recipient,
                    course__term__iexact=term,
                    status=OfferStatus.PENDING.value,
                ).exclude(id=offer.id).update(status=OfferStatus.REJECTED.value)
        messages.success(request, f"Congratulations! You are now a TA for {offer.course.course}.")
    return redirect('offers_v2')

@login_required
def decline_offer_v2(request, offer_id):
    if request.method == 'POST':
        offer = get_object_or_404(Offer, id=offer_id)
        if request.user != offer.recipient:
            messages.error(request, "You are not authorized to decline this offer.")
            return redirect('offers_v2')
        offer.reject()
        messages.info(request, f"You have declined the offer for {offer.course.course}.")
    return redirect('offers_v2')

@login_required
def application_detail_v2(request, application_id):
    app = get_object_or_404(Application, id=application_id)
    
    # Permission Check
    is_student_owner = request.user == app.student
    is_course_professor = request.user == app.course.professor
    
    if not (request.user.is_superuser or is_student_owner or is_course_professor):
        messages.error(request, "You are not authorized to view this application.")
        return redirect('dashboard_v2')
        
    return render(request, 'application_detail_v2.html', {'app': app})


@login_required
def serve_application_resume(request, application_id):
    """Serve the resume snapshot for an application (professor or superuser only)."""
    app = get_object_or_404(Application, id=application_id)
    if not (request.user.is_superuser or request.user == app.course.professor):
        messages.error(request, "You are not authorized to view this resume.")
        return redirect('dashboard_v2')
    if not app.resume:
        messages.warning(request, "No resume was submitted with this application.")
        return redirect('application_detail_v2', application_id=application_id)
    try:
        file_handle = app.resume.open('rb')
        filename = app.resume.name.split('/')[-1] if app.resume.name else 'resume'
        if filename.lower().endswith('.pdf'):
            content_type = 'application/pdf'
        elif filename.lower().endswith('.doc'):
            content_type = 'application/msword'
        elif filename.lower().endswith('.docx'):
            content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        else:
            content_type = 'application/octet-stream'
        response = FileResponse(file_handle, content_type=content_type)
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response
    except (ValueError, OSError):
        messages.error(request, "Resume file could not be found.")
        return redirect('application_detail_v2', application_id=application_id)
