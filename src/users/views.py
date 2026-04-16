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
import re
from .forms import CustomUserUpdateForm, StudentProfileForm, PastCourseForm, PastCourseFormSet
from .models import (
    CustomUser,
    StudentProfile,
    PastCourse,
    Skill,
    ensure_default_skills_exist,
)


class ProfileView(UpdateView):
    model = CustomUser
    form_class = CustomUserUpdateForm
    template_name = 'update.html'
    success_url = reverse_lazy('dashboard')


class StudentProfileView(LoginRequiredMixin, TemplateResponseMixin, View):
    """View for students to edit their profile (resume, past courses)."""
    template_name = 'student_profile.html'
    success_url = reverse_lazy('student_profile')

    def _skills_template_context(self, profile, selected_skill_ids_override=None):
        if not Skill.objects.exists():
            ensure_default_skills_exist()
        qs = Skill.objects.all().order_by('name')
        all_skills = list(qs.values('id', 'name'))
        for s in all_skills:
            s['id'] = str(s['id'])
        if selected_skill_ids_override is not None:
            selected_ids = [str(s) for s in selected_skill_ids_override if s]
            selected_skills = list(Skill.objects.filter(id__in=selected_ids).order_by('name'))
        else:
            selected_ids = [str(sid) for sid in profile.skills.values_list('id', flat=True)]
            selected_skills = list(profile.skills.all().order_by('name'))
        selected_set = set(selected_ids)
        skills_available_to_add = [s for s in qs if str(s.id) not in selected_set]
        return {
            'all_skills': qs,
            'all_skills_json': json.dumps(all_skills),
            'selected_skill_ids': selected_ids,
            'selected_skill_ids_json': json.dumps(selected_ids),
            'selected_skills': selected_skills,
            'skills_available_to_add': skills_available_to_add,
        }

    def get(self, request, *args, **kwargs):
        if request.user.is_professor:
            messages.info(request, 'Professors do not have a student profile.')
            return redirect('dashboard')
        profile, _ = StudentProfile.objects.get_or_create(user=request.user)
        profile_form = StudentProfileForm(instance=profile)
        course_formset = PastCourseFormSet(instance=request.user)
        ctx = {
            'profile_form': profile_form,
            'course_formset': course_formset,
            'profile': profile,
            'profile_complete_for_apply': request.user.has_complete_profile_for_apply(),
        }
        ctx.update(self._skills_template_context(profile))
        return self.render_to_response(ctx)

    def post(self, request, *args, **kwargs):
        if request.user.is_professor:
            return redirect('dashboard')
        profile, _ = StudentProfile.objects.get_or_create(user=request.user)
        profile_form = StudentProfileForm(
            request.POST, request.FILES, instance=profile
        )
        course_formset = PastCourseFormSet(
            request.POST, instance=request.user
        )

        eagleid_val = (request.POST.get('eagleid') or '').strip()
        eagleid_error = None
        if eagleid_val:
            # Numeric input should come through as digits; we enforce exact length.
            if not re.fullmatch(r"\d{8}", eagleid_val):
                eagleid_error = "Eagle ID must be exactly 8 digits."

        if profile_form.is_valid() and course_formset.is_valid():
            # Keep existing files: Django clears FileFields when not in request.FILES
            old_resume = profile.resume
            old_cv = profile.cv
            profile = profile_form.save(commit=False)
            if not request.FILES.get('resume'):
                profile.resume = old_resume
            if not request.FILES.get('cv'):
                profile.cv = old_cv
            if request.POST.get('remove_resume') == '1':
                profile.resume = None
            if request.POST.get('remove_cv') == '1':
                profile.cv = None
            profile.save()
            course_formset.save()
            skill_ids = request.POST.getlist('skills', [])
            profile.skills.set(Skill.objects.filter(id__in=skill_ids))
            if eagleid_error:
                messages.error(request, eagleid_error)
            else:
                # Save Eagle ID on user (empty = clear it)
                request.user.eagleid = int(eagleid_val) if eagleid_val else 0
                request.user.save(update_fields=['eagleid'])
                messages.success(request, 'Profile updated successfully.')
                return redirect(self.success_url)
        selected_ids = request.POST.getlist('skills', [])
        ctx = {
            'profile_form': profile_form,
            'course_formset': course_formset,
            'profile': profile,
            'profile_complete_for_apply': request.user.has_complete_profile_for_apply(),
            'eagleid_error': eagleid_error,
        }
        ctx.update(self._skills_template_context(profile, selected_skill_ids_override=selected_ids))
        return self.render_to_response(ctx)


def serve_resume(request):
    """Serve the current user's resume."""
    if not request.user.is_authenticated:
        messages.error(request, 'Please log in to view your resume.')
        return redirect('users:login')
    if request.user.is_professor:
        messages.info(request, 'Professors do not have a student resume.')
        return redirect('dashboard')
    try:
        profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        messages.info(request, 'You have not created a student profile yet.')
        return redirect('student_profile')
    if not profile.resume:
        messages.warning(request, 'You have not uploaded a resume yet.')
        return redirect('student_profile')
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
        return redirect('student_profile')


def serve_cv(request):
    """Serve the current user's CV."""
    if not request.user.is_authenticated:
        messages.error(request, 'Please log in to view your CV.')
        return redirect('users:login')
    if request.user.is_professor:
        messages.info(request, 'Professors do not have a student CV.')
        return redirect('dashboard')
    try:
        profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        messages.info(request, 'You have not created a student profile yet.')
        return redirect('student_profile')
    if not profile.cv:
        messages.warning(request, 'You have not uploaded a CV yet.')
        return redirect('student_profile')
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
        return redirect('student_profile')


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
