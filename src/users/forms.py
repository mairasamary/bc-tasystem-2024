from datetime import date
from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserChangeForm
from .models import CustomUser, StudentProfile, PastCourse, Skill, PREDEFINED_COURSES, GRADE_CHOICES

COURSE_CHOICES = [('', '-- Select a course --')] + [(c, c) for c in PREDEFINED_COURSES] + [('__custom__', 'Custom elective (enter name below)')]


class CustomUserUpdateForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ['eagleid']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields['password']


INPUT_CLASS = 'w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-bc-maroon focus:border-bc-maroon'

class PastCourseForm(forms.ModelForm):
    course_selection = forms.ChoiceField(
        choices=COURSE_CHOICES, required=False, label='Course',
        widget=forms.Select(attrs={'class': INPUT_CLASS})
    )
    custom_course_name = forms.CharField(
        max_length=200, required=False, label='Custom course name',
        widget=forms.TextInput(attrs={'placeholder': 'Enter elective name', 'class': INPUT_CLASS})
    )
    grade = forms.ChoiceField(
        choices=GRADE_CHOICES, required=False, label='Grade',
        widget=forms.Select(attrs={'class': INPUT_CLASS})
    )

    class Meta:
        model = PastCourse
        fields = ['grade']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if self.instance.course_name in PREDEFINED_COURSES:
                self.fields['course_selection'].initial = self.instance.course_name
            else:
                self.fields['course_selection'].initial = '__custom__'
                self.fields['custom_course_name'].initial = self.instance.course_name

    def clean(self):
        data = super().clean()
        selection = data.get('course_selection')
        custom = (data.get('custom_course_name') or '').strip()
        grade = data.get('grade')
        if not selection and not custom and not grade:
            return data
        if selection == '__custom__':
            if not custom:
                self.add_error('custom_course_name', 'Please enter the course name.')
            else:
                data['course_name'] = custom
        elif selection:
            data['course_name'] = selection
        else:
            self.add_error('course_selection', 'Please select a course or enter a custom one.')
        if not grade:
            self.add_error('grade', 'Please select a grade.')
        return data

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.course_name = self.cleaned_data.get('course_name', '') or obj.course_name
        if commit:
            obj.save()
        return obj


class PastCourseFormSetBase(forms.BaseInlineFormSet):
    def save(self, commit=True):
        """Skip saving forms that have no course_name (empty add rows)."""
        if not commit:
            return super().save(commit=False)
        instances = []
        for form in self.forms:
            if form in self.deleted_forms:
                if form.instance.pk:
                    form.instance.delete()
            elif form.cleaned_data and form.cleaned_data.get('course_name'):
                obj = form.save(commit=False)
                obj.save()
                instances.append(obj)
        return instances


PastCourseFormSet = inlineformset_factory(
    CustomUser, PastCourse, form=PastCourseForm, formset=PastCourseFormSetBase,
    extra=0, can_delete=True
)


def _graduation_year_choices():
    year = date.today().year
    return [('', '-- Select year --')] + [(y, f'Class of {y}') for y in range(year, year + 4)]


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['profile_photo', 'resume', 'cv', 'graduation_year', 'skills']
        widgets = {
            'profile_photo': forms.FileInput(attrs={'accept': 'image/*'}),
            'resume': forms.FileInput(attrs={'accept': '.pdf,.doc,.docx'}),
            'cv': forms.FileInput(attrs={'accept': '.pdf,.doc,.docx'}),
            'graduation_year': forms.Select(attrs={'class': INPUT_CLASS}),
            'skills': forms.CheckboxSelectMultiple(attrs={'class': 'skill-checkbox'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['graduation_year'].widget.choices = _graduation_year_choices()


CHECKBOX_CLASS = "h-4 w-4 rounded border-gray-300 text-bc-navy focus:ring-bc-navy"


class StudentEmploymentOnboardingForm(forms.ModelForm):
    """Self-reported completion of BC student employment onboarding forms."""

    class Meta:
        model = StudentProfile
        fields = [
            "onboarding_done_required_form",
            "onboarding_done_i9",
            "onboarding_done_payroll_statement",
            "onboarding_done_w4",
            "onboarding_done_m4",
            "onboarding_done_direct_deposit",
        ]
        widgets = {
            "onboarding_done_required_form": forms.CheckboxInput(attrs={"class": CHECKBOX_CLASS}),
            "onboarding_done_i9": forms.CheckboxInput(attrs={"class": CHECKBOX_CLASS}),
            "onboarding_done_payroll_statement": forms.CheckboxInput(attrs={"class": CHECKBOX_CLASS}),
            "onboarding_done_w4": forms.CheckboxInput(attrs={"class": CHECKBOX_CLASS}),
            "onboarding_done_m4": forms.CheckboxInput(attrs={"class": CHECKBOX_CLASS}),
            "onboarding_done_direct_deposit": forms.CheckboxInput(attrs={"class": CHECKBOX_CLASS}),
        }
