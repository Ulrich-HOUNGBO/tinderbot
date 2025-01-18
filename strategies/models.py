from uuid import uuid4

from django.db import models

from tinderbot import settings


# Create your models here.
class Strategy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    days_number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    proxy = models.ForeignKey(
        "proxies.Proxy", on_delete=models.DO_NOTHING, null=True, blank=True
    )

    def __repr__(self):
        return self.id
