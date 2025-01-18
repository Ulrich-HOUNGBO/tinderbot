import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models


# Create your models here.


class BotSettings(models.Model):
    id = models.UUIDField(
        primary_key=True, editable=False, unique=True, null=False, default=uuid.uuid4
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    min_swipe_times = models.IntegerField(default=0)
    max_swipe_times = models.IntegerField(default=100)
    min_right_swipe_percentage = models.FloatField(default=0.5)
    max_right_swipe_percentage = models.FloatField(default=0.5)
    status = models.CharField(max_length=20, default="Stopped")

    scheduled_time = models.TimeField(null=True, blank=True)
    scheduled_time_2 = models.TimeField(null=True, blank=True)
    strategy = models.ForeignKey("strategies.Strategy", on_delete=models.CASCADE)
    related_day = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return self.id
