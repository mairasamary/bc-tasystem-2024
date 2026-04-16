from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0008_remove_pastcourse_grade_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="studentprofile",
            name="bc_student_worker",
            field=models.BooleanField(
                default=False,
                help_text="If you have been a BC student worker before, you likely already completed onboarding documents.",
                verbose_name="I was a BC student worker before (skip onboarding checklist)",
            ),
        ),
    ]

