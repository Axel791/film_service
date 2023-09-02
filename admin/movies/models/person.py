from django.db import models
from django.utils.translation import gettext_lazy as _

from movies.models.film import FilmWork
from movies.models.mixins import TimeStampedMixin, UUIDMixin


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.CharField(verbose_name=_("full name"), max_length=250)

    def __str__(self):
        return self.full_name

    class Meta:
        db_table = 'content"."person'
        verbose_name = _("Human")
        verbose_name_plural = _("People")


class PersonFilmWork(UUIDMixin):
    person_id = models.ForeignKey(
        Person, on_delete=models.CASCADE, related_name="persons"
    )
    film_work_id = models.ForeignKey(
        FilmWork, on_delete=models.CASCADE, related_name="film_persons"
    )
    role = models.CharField(verbose_name=_("Role"), max_length=50)
    crated = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'content"."person_film_work'
        verbose_name = _("Film employee")
        verbose_name_plural = _("Film employees")
        constraints = [
            models.UniqueConstraint(
                fields=["person_id", "film_work_id"], name="person_film_work_id_index"
            )
        ]
