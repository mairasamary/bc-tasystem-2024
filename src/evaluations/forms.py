from django import forms
from users.models import CustomUser

from .models import TAEvaluation, RATING_CHOICES


class TAEvaluationForm(forms.ModelForm):
    class Meta:
        model = TAEvaluation
        fields = [
            "ta",
            "course",
            "rating_punctuality",
            "rating_communication",
            "rating_technical",
            "rating_professionalism",
            "rating_overall",
            "feedback",
        ]
        widgets = {
            "ta": forms.Select(attrs={"class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-bc-maroon focus:border-bc-maroon", "required": True}),
            "course": forms.Select(attrs={"class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-bc-maroon focus:border-bc-maroon", "required": True}),
            "rating_punctuality": forms.RadioSelect(choices=RATING_CHOICES),
            "rating_communication": forms.RadioSelect(choices=RATING_CHOICES),
            "rating_technical": forms.RadioSelect(choices=RATING_CHOICES),
            "rating_professionalism": forms.RadioSelect(choices=RATING_CHOICES),
            "rating_overall": forms.RadioSelect(choices=RATING_CHOICES),
            "feedback": forms.Textarea(attrs={"rows": 4, "placeholder": "Optional written feedback...", "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-bc-maroon focus:border-bc-maroon"}),
        }

    def __init__(self, *args, **kwargs):
        self.professor = kwargs.pop("professor", None)
        self.readonly_ta_course = kwargs.pop("readonly_ta_course", False)
        super().__init__(*args, **kwargs)
        if self.professor:
            tas_qs = CustomUser.objects.filter(
                course_working_for__professor=self.professor
            ).distinct()
            # Allow evaluating courses even after an admin closes the semester.
            # The admin "close" action currently flips `Course.is_active/status` flags,
            # but evaluations should remain available.
            courses_qs = self.professor.courses.all()
            self.fields["ta"].queryset = tas_qs
            self.fields["course"].queryset = courses_qs
            self.fields["ta"].empty_label = None
            self.fields["course"].empty_label = None
        if self.readonly_ta_course:
            self.fields["ta"].disabled = True
            self.fields["course"].disabled = True
        for name in ["rating_punctuality", "rating_communication", "rating_technical", "rating_professionalism", "rating_overall"]:
            self.fields[name].choices = [
                c for c in self.fields[name].choices if c[0] != "" and c[0] is not None
            ]

