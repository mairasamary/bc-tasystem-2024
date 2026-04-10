from django.db import migrations, models

import applications.models


class Migration(migrations.Migration):

    dependencies = [
        ("applications", "0003_application_courses_snapshot_application_other_notes_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="application",
            name="profile_photo",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to=applications.models.application_profile_photo_upload_path,
            ),
        ),
    ]
