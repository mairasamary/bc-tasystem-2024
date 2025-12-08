
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from courses.models import Course
from applications.models import Application, ApplicationStatus
from offers.models import Offer, OfferStatus

User = get_user_model()

def home(request):
    courses = Course.objects.all()
    context = {'courses': courses}
    return render(request, 'home.html', context)

@login_required
def admin_dashboard_v2(request):
    # Stats
    pending_apps_count = Application.objects.filter(status=ApplicationStatus.PENDING.value).count()
    total_offers_count = Offer.objects.count()
    active_courses_count = Course.objects.filter(status=True).count()
    total_users_count = User.objects.count()

    # Lists
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

@login_required
def applications_list_v2(request):
    apps = Application.objects.select_related('student', 'course').order_by('-id')
    return render(request, 'applications_v2.html', {'apps': apps})

@login_required
def offers_list_v2(request):
    offers = Offer.objects.select_related('recipient', 'course').order_by('-created_at')
    return render(request, 'offers_v2.html', {'offers': offers})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from applications.models import Application, ApplicationStatus

@login_required
def courses_list_v2(request):
    query = request.GET.get('q')
    courses = Course.objects.all().order_by('course')
    
    if query:
        courses = courses.filter(
            Q(course__icontains=query) | 
            Q(course_title__icontains=query) |
            Q(instructor_first_name__icontains=query) |
            Q(instructor_last_name__icontains=query)
        )
    
    # Get IDs of courses the current user has already applied to
    if not request.user.is_professor(): # Assuming is_professor() method exists based on model view
        applied_course_ids = Application.objects.filter(student=request.user).values_list('course_id', flat=True)
    else:
        applied_course_ids = []
        
    return render(request, 'courses_v2.html', {
        'courses': courses,
        'applied_course_ids': applied_course_ids
    })

@login_required
def apply_to_course_v2(request, course_id):
    if request.method == 'POST':
        course = get_object_or_404(Course, id=course_id)
        if request.user.is_professor():
             messages.error(request, "Professors cannot apply for TA positions.")
             return redirect('courses_v2')
        
        # Check if already applied
        if Application.objects.filter(student=request.user, course=course).exists():
             messages.warning(request, "You have already applied to this course.")
             return redirect('courses_v2')

        # Create application
        Application.objects.create(
            student=request.user,
            course=course,
            status=ApplicationStatus.PENDING.value
        )
        messages.success(request, f"Successfully applied to {course.course}.")
        
    return redirect('courses_v2')

@login_required
def make_offer_v2(request, application_id):
    if request.method == 'POST':
        if not request.user.is_professor():
            messages.error(request, "Only professors can make offers.")
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
def accept_offer_v2(request, offer_id):
    if request.method == 'POST':
        offer = get_object_or_404(Offer, id=offer_id)
        
        if request.user != offer.recipient:
             messages.error(request, "You are not authorized to accept this offer.")
             return redirect('offers_v2')
             
        # Use model method for consistent logic
        offer.accept()
        
        messages.success(request, f"Congratulations! You are now a TA for {offer.course.course}.")
        
    return redirect('offers_v2')

@login_required
def decline_offer_v2(request, offer_id):
    if request.method == 'POST':
        offer = get_object_or_404(Offer, id=offer_id)
        
        if request.user != offer.recipient:
             messages.error(request, "You are not authorized to decline this offer.")
             return redirect('offers_v2')
             
        # Use model method for consistent logic
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
