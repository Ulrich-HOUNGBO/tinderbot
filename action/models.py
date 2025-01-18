import uuid

from django.db import models


# Create your models here.

class Action(models.Model):
    id = models.UUIDField(
        primary_key=True, editable=False, unique=True, null=False, default=uuid.uuid4
    )
    type = models.CharField(max_length=255, default="swiping")
    status = models.CharField(max_length=20, default="Stopped")
    scheduled_time = models.TimeField(null=True, blank=True)
    scheduled_time_2 = models.TimeField(null=True, blank=True)
    min_swipe_times = models.IntegerField(null=True, blank=True)
    max_swipe_times = models.IntegerField(null=True, blank=True)
    min_right_swipe_percentage = models.FloatField(null=True, blank=True)
    max_right_swipe_percentage = models.FloatField(null=True, blank=True)
    bio_list = models.TextField(null=True, blank=True)
    insta_list = models.TextField(null=True, blank=True)
    strategy = models.ForeignKey("strategies.Strategy", on_delete=models.CASCADE)
    related_day = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
