import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class UUIDMixin(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    class Meta:
        abstract = True


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(
        auto_now_add=True, verbose_name=_("created")
    )
    modified = models.DateTimeField(
        auto_now=True, verbose_name=_("modified")
    )

    class Meta:
        abstract = True
