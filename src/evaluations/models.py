from django.db import models
from users.models import CustomUser
from courses.models import Course


RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]


class TAEvaluation(models.Model):
    reviewer = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="ta_evaluations_given",
    )
    ta = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="ta_evaluations_received",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="ta_evaluations",
    )

    rating_punctuality = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    rating_communication = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    rating_technical = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    rating_professionalism = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    rating_overall = models.PositiveSmallIntegerField(choices=RATING_CHOICES)

    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [["reviewer", "ta", "course"]]
        ordering = ["-created_at"]

    @property
    def average_rating(self):
        ratings = [
            self.rating_punctuality,
            self.rating_communication,
            self.rating_technical,
            self.rating_professionalism,
            self.rating_overall,
        ]
        return round(sum(ratings) / len(ratings), 1)
