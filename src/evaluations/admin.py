from django.contrib import admin
from .models import TAEvaluation


@admin.register(TAEvaluation)
class TAEvaluationAdmin(admin.ModelAdmin):
    list_display = ["ta", "course", "reviewer", "get_avg_rating", "created_at"]

    @admin.display(description="Avg Rating")
    def get_avg_rating(self, obj):
        return obj.average_rating
    list_filter = ["course", "reviewer"]
    search_fields = ["ta__first_name", "ta__last_name", "feedback"]
