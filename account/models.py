import uuid

from django.conf import settings
from django.db import models


# Create your models here.


class Account(models.Model):
    id = models.UUIDField(
        primary_key=True, editable=False, unique=True, null=False, default=uuid.uuid4
    )
    title = models.CharField(max_length=255)
    modele = models.ForeignKey(
        "modeles.Modeles", on_delete=models.DO_NOTHING, null=True, blank=True
    )
    device_id = models.CharField(max_length=255, null=True, blank=True)
    token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    strategy = models.ForeignKey(
        "strategies.Strategy", on_delete=models.DO_NOTHING, null=True, blank=True
    )
    progress = models.IntegerField(default=1)
    insta_username = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, default="standby")
    min_age = models.IntegerField(default=18)
    max_age = models.IntegerField(default=30)
    distance = models.IntegerField(default=20)
    timezone_field = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
