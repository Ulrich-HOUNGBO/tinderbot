import uuid

from django.db import models

from tinderbot import settings


# Create your models here.
class Modeles(models.Model):
    id = models.UUIDField(
        primary_key=True, editable=False, unique=True, null=False, default=uuid.uuid4
    )
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return self.id
