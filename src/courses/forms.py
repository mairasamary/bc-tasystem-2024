from django import forms
from .models import Course
from users.models import CustomUser


TAILWIND_INPUT = 'block w-full rounded-lg border-2 border-gray-300 bg-white p-2.5 text-sm text-gray-900 focus:ring-bc-maroon focus:border-bc-maroon transition-all'
TAILWIND_SELECT = 'block w-full rounded-lg border-2 border-gray-300 bg-white p-2.5 text-sm text-gray-900 focus:ring-bc-maroon focus:border-bc-maroon transition-all'
TAILWIND_TEXTAREA = 'block w-full rounded-lg border-2 border-gray-300 bg-white p-2.5 text-sm text-gray-900 focus:ring-bc-maroon focus:border-bc-maroon transition-all'


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            'term', 'class_type', 'course', 'section', 'course_title',
            'professor', 'room_name', 'timeslot',
            'max_enroll', 'room_size', 'num_tas',
            'description',
        ]
        widgets = {
            'term': forms.TextInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'e.g. Fall 2025'}),
            'class_type': forms.Select(attrs={'class': TAILWIND_SELECT}, choices=[
                ('Lecture', 'Lecture'),
                ('Discussion', 'Discussion'),
                ('Lab', 'Lab'),
            ]),
            'course': forms.TextInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'e.g. CSCI3383'}),
            'section': forms.TextInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'e.g. 01'}),
            'course_title': forms.TextInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'e.g. Algorithms'}),
            'professor': forms.Select(attrs={'class': TAILWIND_SELECT}),
            'room_name': forms.TextInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'e.g. Fulton 250'}),
            'timeslot': forms.TextInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'e.g. MWF 11:00-11:50'}),
            'max_enroll': forms.NumberInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'e.g. 30', 'min': 0}),
            'room_size': forms.NumberInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'e.g. 40', 'min': 0}),
            'num_tas': forms.NumberInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'e.g. 2', 'min': 1}),
            'description': forms.Textarea(attrs={'class': TAILWIND_TEXTAREA, 'rows': 3, 'placeholder': 'Course description (optional)'}),
        }
        labels = {
            'class_type': 'Class Type',
            'course': 'Course Code',
            'course_title': 'Course Title',
            'room_name': 'Room',
            'timeslot': 'Time Slot',
            'max_enroll': 'Max Enrollment',
            'room_size': 'Room Size',
            'num_tas': 'Number of TAs Needed',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['professor'].queryset = CustomUser.objects.filter(professor=True).order_by('last_name', 'first_name')
        self.fields['professor'].required = False
        self.fields['class_type'] = forms.ChoiceField(
            choices=[('Lecture', 'Lecture'), ('Discussion', 'Discussion'), ('Lab', 'Lab')],
            widget=forms.Select(attrs={'class': TAILWIND_SELECT}),
            label='Class Type',
        )
