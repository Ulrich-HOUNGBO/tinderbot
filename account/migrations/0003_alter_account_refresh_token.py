# Generated by Django 5.0.6 on 2024-09-25 06:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0002_account_device_id_account_process_day_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="account",
            name="refresh_token",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
