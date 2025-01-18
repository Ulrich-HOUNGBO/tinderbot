import uuid

from django.db import models

from tinderbot import settings


# Create your models here.


class Proxy(models.Model):
    id = models.UUIDField(
        primary_key=True, editable=False, unique=True, null=False, default=uuid.uuid4
    )
    name = models.CharField(max_length=255, null=True, blank=True)
    host = models.CharField(max_length=255)
    port = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    rotation_link = models.URLField(null=True, blank=True)
    type = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __repr__(self):
        return self.id
