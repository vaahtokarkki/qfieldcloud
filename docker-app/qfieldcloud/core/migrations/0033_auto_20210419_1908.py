# Generated by Django 3.2 on 2021-04-19 19:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    def add_created_by(apps, schema_editor):
        Delta = apps.get_model("core", "Delta")

        for delta in Delta.objects.all():
            delta.created_by = delta.project.owner
            delta.save()

    dependencies = [
        ("core", "0032_auto_20210419_1011"),
    ]

    operations = [
        migrations.AddField(
            model_name="delta",
            name="created_by",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="uploaded_deltas",
                to="core.user",
                null=True,
            ),
        ),
        migrations.RunPython(add_created_by, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="delta",
            name="created_by",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="uploaded_deltas",
                to="core.user",
            ),
        ),
    ]