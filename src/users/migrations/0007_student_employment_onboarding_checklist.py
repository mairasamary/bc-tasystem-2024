# Generated manually for student employment onboarding self-report fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0006_add_graduation_year"),
    ]

    operations = [
        migrations.AddField(
            model_name="studentprofile",
            name="onboarding_done_direct_deposit",
            field=models.BooleanField(
                default=False,
                verbose_name="Direct Deposit Enrollment Instructions",
            ),
        ),
        migrations.AddField(
            model_name="studentprofile",
            name="onboarding_done_i9",
            field=models.BooleanField(default=False, verbose_name="Form I-9"),
        ),
        migrations.AddField(
            model_name="studentprofile",
            name="onboarding_done_m4",
            field=models.BooleanField(
                default=False,
                verbose_name="M-4 (Massachusetts Withholding Form)",
            ),
        ),
        migrations.AddField(
            model_name="studentprofile",
            name="onboarding_done_payroll_statement",
            field=models.BooleanField(
                default=False,
                verbose_name="Payroll Form Statement (Student Hours at Boston College)",
            ),
        ),
        migrations.AddField(
            model_name="studentprofile",
            name="onboarding_done_required_form",
            field=models.BooleanField(
                default=False,
                verbose_name="Required Onboarding Form for New Student Employees",
            ),
        ),
        migrations.AddField(
            model_name="studentprofile",
            name="onboarding_done_w4",
            field=models.BooleanField(
                default=False,
                verbose_name="W-4 (Federal Withholding Form)",
            ),
        ),
    ]
