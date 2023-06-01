from movies.models.mixins import UUIDMixin, TimeStampedMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from movies.models.film import FilmWork


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(verbose_name=_('name'), max_length=255)
    description = models.TextField(verbose_name=_('description'), blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "content\".\"genre"
        verbose_name = _("Genre")
        verbose_name_plural = _("Genres")


class GenreFilmWork(UUIDMixin):
    genre_id = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        related_name='genres'
    )
    film_work_id = models.ForeignKey(
        FilmWork,
        on_delete=models.CASCADE,
        related_name='film_genres'
    )
    crated = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"genre_film_work"
        verbose_name = 'Genre film'
        verbose_name_plural = _('Genres film')
        constraints = [
            models.UniqueConstraint(
                fields=['genre_id', 'film_work_id'],
                name="genre_film_work_id_index"
            )
        ]
