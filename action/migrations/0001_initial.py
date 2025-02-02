# Generated by Django 5.0.6 on 2024-10-27 20:38

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("strategies", "0005_alter_strategy_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="Action",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("type", models.CharField(default="swiping", max_length=255)),
                ("status", models.CharField(default="Stopped", max_length=20)),
                ("scheduled_time", models.TimeField(blank=True, null=True)),
                ("scheduled_time_2", models.TimeField(blank=True, null=True)),
                ("min_swipe_times", models.IntegerField(blank=True, null=True)),
                ("max_swipe_times", models.IntegerField(blank=True, null=True)),
                (
                    "min_right_swipe_percentage",
                    models.FloatField(blank=True, null=True),
                ),
                (
                    "max_right_swipe_percentage",
                    models.FloatField(blank=True, null=True),
                ),
                ("bio_list", models.TextField(blank=True, null=True)),
                ("insta_list", models.TextField(blank=True, null=True)),
                ("related_day", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "strategy",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="strategies.strategy",
                    ),
                ),
            ],
        ),
    ]
