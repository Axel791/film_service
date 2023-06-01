from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.list import BaseListView
from django.views.generic.detail import BaseDetailView
from django.contrib.postgres.aggregates import ArrayAgg

from movies.models.film import FilmWork
from movies.models.person import PersonFilmWork


class FilmWorkApiMixin:
    model = FilmWork
    http_method_names = ['get']

    @staticmethod
    def _aggregate_film_employee(role: str):
        return ArrayAgg(
            'film_persons__person_id__full_name',
            filter=Q(film_persons__role=role),
            distinct=True
        )

    def get_queryset(self):
        queryset = FilmWork.objects.values(
            'id', 'tittle', 'description', 'created', 'rating', 'type'
        ).annotate(
            genres=ArrayAgg('film_genres__genre_id__name', distinct=True),
            actors=self._aggregate_film_employee(role=PersonFilmWork.Role.ACTOR),
            directors=self._aggregate_film_employee(role=PersonFilmWork.Role.DIRECTOR),
            operators=self._aggregate_film_employee(role=PersonFilmWork.Role.OPERATOR),
            screenwriters=self._aggregate_film_employee(role=PersonFilmWork.Role.SCREENWRITER),
        ).order_by('tittle')

        return queryset

    @staticmethod
    def render_to_response(context, **kwargs):
        return JsonResponse(context)


class DetailFilmView(FilmWorkApiMixin, BaseDetailView):

    def get_context_data(self, **kwargs):
        return self.object


class ListFilmView(FilmWorkApiMixin, BaseListView):
    PAGINATE_BY = 3

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset()
        paginator, page, queryset, is_paginated = self.paginate_queryset(
            queryset,
            self.PAGINATE_BY
        )

        previous_page = page.previous_page_number() if page.has_previous() else None
        next_page = page.next_page_number() if page.has_next() else None

        return {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'prev': previous_page,
            'next': next_page,
            'results': list(queryset)
        }
