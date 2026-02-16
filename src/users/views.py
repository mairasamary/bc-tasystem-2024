import json
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import inlineformset_factory
from django.http import FileResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import View
from django.views.generic.edit import UpdateView
from django.views.generic.base import TemplateResponseMixin
from .forms import CustomUserUpdateForm, StudentProfileForm, PastCourseForm, PastCourseFormSet
from .models import CustomUser, StudentProfile, PastCourse, Skill


class ProfileView(UpdateView):
    model = CustomUser
    form_class = CustomUserUpdateForm
    template_name = 'update.html'
    success_url = reverse_lazy('dashboard_v2')


class StudentProfileView(LoginRequiredMixin, TemplateResponseMixin, View):
    """View for students to edit their profile (resume, past courses)."""
    template_name = 'student_profile.html'
    success_url = reverse_lazy('student_profile_v2')

    def get(self, request, *args, **kwargs):
        if request.user.is_professor:
            messages.info(request, 'Professors do not have a student profile.')
            return redirect('dashboard_v2')
        profile, _ = StudentProfile.objects.get_or_create(user=request.user)
        profile_form = StudentProfileForm(instance=profile)
        course_formset = PastCourseFormSet(instance=request.user)
        all_skills = list(Skill.objects.all().values('id', 'name'))
        for s in all_skills:
            s['id'] = str(s['id'])
        return self.render_to_response({
            'profile_form': profile_form,
            'course_formset': course_formset,
            'profile': profile,
            'all_skills': Skill.objects.all(),
            'all_skills_json': json.dumps(all_skills),
            'selected_skill_ids': [str(sid) for sid in profile.skills.values_list('id', flat=True)],
            'selected_skill_ids_json': json.dumps([str(sid) for sid in profile.skills.values_list('id', flat=True)]),
            'selected_skills': list(profile.skills.all()),
        })

    def post(self, request, *args, **kwargs):
        if request.user.is_professor:
            return redirect('dashboard_v2')
        profile, _ = StudentProfile.objects.get_or_create(user=request.user)
        profile_form = StudentProfileForm(
            request.POST, request.FILES, instance=profile
        )
        course_formset = PastCourseFormSet(
            request.POST, instance=request.user
        )
        if profile_form.is_valid() and course_formset.is_valid():
            profile_form.save()
            course_formset.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect(self.success_url)
        selected_ids = request.POST.getlist('skills', [])
        selected_skills = list(Skill.objects.filter(id__in=selected_ids))
        all_skills = list(Skill.objects.all().values('id', 'name'))
        for s in all_skills:
            s['id'] = str(s['id'])
        return self.render_to_response({
            'profile_form': profile_form,
            'course_formset': course_formset,
            'profile': profile,
            'all_skills': Skill.objects.all(),
            'all_skills_json': json.dumps(all_skills),
            'selected_skill_ids': selected_ids,
            'selected_skill_ids_json': json.dumps(selected_ids),
            'selected_skills': selected_skills,
        })


def serve_resume(request):
    """Serve the current user's resume."""
    if not request.user.is_authenticated:
        messages.error(request, 'Please log in to view your resume.')
        return redirect('users:login')
    if request.user.is_professor:
        messages.info(request, 'Professors do not have a student resume.')
        return redirect('dashboard_v2')
    try:
        profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        messages.info(request, 'You have not created a student profile yet.')
        return redirect('student_profile_v2')
    if not profile.resume:
        messages.warning(request, 'You have not uploaded a resume yet.')
        return redirect('student_profile_v2')
    try:
        file_handle = profile.resume.open('rb')
        filename = profile.resume.name.split('/')[-1] if profile.resume.name else 'resume'
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
        messages.error(request, 'Your resume file could not be found. Please re-upload your resume.')
        return redirect('student_profile_v2')


def serve_cv(request):
    """Serve the current user's CV."""
    if not request.user.is_authenticated:
        messages.error(request, 'Please log in to view your CV.')
        return redirect('users:login')
    if request.user.is_professor:
        messages.info(request, 'Professors do not have a student CV.')
        return redirect('dashboard_v2')
    try:
        profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        messages.info(request, 'You have not created a student profile yet.')
        return redirect('student_profile_v2')
    if not profile.cv:
        messages.warning(request, 'You have not uploaded a CV yet.')
        return redirect('student_profile_v2')
    try:
        file_handle = profile.cv.open('rb')
        filename = profile.cv.name.split('/')[-1] if profile.cv.name else 'cv'
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
        messages.error(request, 'Your CV file could not be found. Please re-upload your CV.')
        return redirect('student_profile_v2')


def serve_profile_photo(request):
    """Serve the current user's profile photo."""
    from django.http import HttpResponse
    if not request.user.is_authenticated:
        return HttpResponse(status=404)
    try:
        profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        return HttpResponse(status=404)
    if not profile.profile_photo:
        return HttpResponse(status=404)
    try:
        file_handle = profile.profile_photo.open('rb')
        data = file_handle.read()
        filename = (profile.profile_photo.name or '').lower()
        if filename.endswith('.png'):
            content_type = 'image/png'
        elif filename.endswith('.gif'):
            content_type = 'image/gif'
        elif filename.endswith('.webp'):
            content_type = 'image/webp'
        else:
            content_type = 'image/jpeg'
        return HttpResponse(data, content_type=content_type)
    except (ValueError, OSError):
        return HttpResponse(status=404)
