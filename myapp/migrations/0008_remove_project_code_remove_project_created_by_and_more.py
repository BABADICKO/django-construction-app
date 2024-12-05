# Generated by Django 5.1.3 on 2024-12-04 11:16

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0007_auto_20241203_1733"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="project",
            name="code",
        ),
        migrations.RemoveField(
            model_name="project",
            name="created_by",
        ),
        migrations.RemoveField(
            model_name="project",
            name="location",
        ),
        migrations.RemoveField(
            model_name="project",
            name="manager",
        ),
        migrations.RemoveField(
            model_name="project",
            name="progress",
        ),
        migrations.RemoveField(
            model_name="project",
            name="total_budget",
        ),
        migrations.AddField(
            model_name="materialtransaction",
            name="warehouse",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="transactions",
                to="myapp.warehouse",
            ),
        ),
        migrations.AlterField(
            model_name="materialtransaction",
            name="date",
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name="materialtransaction",
            name="project",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="material_transactions",
                to="myapp.project",
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="project",
            name="status",
            field=models.CharField(
                choices=[
                    ("ACTIVE", "Active"),
                    ("COMPLETED", "Completed"),
                    ("ON_HOLD", "On Hold"),
                    ("CANCELLED", "Cancelled"),
                ],
                default="ACTIVE",
                max_length=20,
            ),
        ),
    ]
