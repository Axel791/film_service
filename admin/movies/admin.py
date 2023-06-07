from django.contrib import admin
from movies.models.film import FilmWork
from movies.models.genre import Genre, GenreFilmWork
from movies.models.person import Person, PersonFilmWork


class GenreFilmWorkInline(admin.TabularInline):
    model = GenreFilmWork
    autocomplete_fields = ('genre_id', 'film_work_id')


class PersonFilmWorkInline(admin.TabularInline):
    model = PersonFilmWork
    autocomplete_fields = ('person_id', 'film_work_id')


@admin.register(FilmWork)
class FilmWorkAdmin(admin.ModelAdmin):
    inlines = (GenreFilmWorkInline, PersonFilmWorkInline)

    list_display = ('id', 'title', 'type', 'rating', 'created', 'modified')
    list_filter = ('type', 'rating')
    search_fields = ('title', 'description', 'id')


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ('film_work_id', 'genre_id')
    list_display = ("name", "description")


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    search_fields = ('person_id', 'film_work_id')
    list_display = ("full_name", )
