from django import forms
from .models import Application

APPLY_INPUT_CLASS = (
    'block w-full rounded-md border-0 p-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 '
    'placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6'
)

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['why_this_course', 'relevant_experience', 'other_notes']
        widgets = {
            'why_this_course': forms.Textarea(attrs={
                'class': APPLY_INPUT_CLASS,
                'rows': 3,
                'maxlength': 500,
                'placeholder': 'Why do you want to be a TA for this course?',
            }),
            'relevant_experience': forms.Textarea(attrs={
                'class': APPLY_INPUT_CLASS,
                'rows': 3,
                'maxlength': 500,
                'placeholder': 'Relevant experience (courses taken, prior TA/tutoring, etc.)',
            }),
            'other_notes': forms.Textarea(attrs={
                'class': APPLY_INPUT_CLASS,
                'rows': 2,
                'maxlength': 300,
                'placeholder': 'Any other notes (optional)',
            }),
        }
        labels = {
            'why_this_course': 'Why this course?',
            'relevant_experience': 'Relevant experience',
            'other_notes': 'Other notes',
        }
        help_texts = {
            'why_this_course': 'Max 500 characters.',
            'relevant_experience': 'Max 500 characters.',
            'other_notes': 'Max 300 characters. Optional.',
        }
