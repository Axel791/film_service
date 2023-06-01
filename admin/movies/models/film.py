from django.db import models
from movies.models.mixins import UUIDMixin, TimeStampedMixin
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class FilmWork(UUIDMixin, TimeStampedMixin):

    class FilmType(models.TextChoices):
        TV_SHOW = "TV", _("TV Show")
        FILM = "FM", _("FIlm")

    tittle = models.CharField(verbose_name=_('title'), max_length=250)
    description = models.TextField(verbose_name=_('description'), blank=True)
    rating = models.FloatField(
        verbose_name=_('rating'),
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    type = models.CharField(
        verbose_name=_('type'),
        max_length=2,
        choices=FilmType.choices
    )

    def __str__(self):
        return self.tittle

    class Meta:
        db_table = "content\".\"film_work"
        verbose_name = _('Film')
        verbose_name_plural = _('Films')
        indexes = [
            models.Index(
                fields=['rating', 'created'],
                name="fim_created_date_rating_index"
            )
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['tittle'],
                name="film_title_index"
            )
        ]
