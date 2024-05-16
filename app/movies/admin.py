from django.contrib import admin

from .models import Filmwork, Genre, GenreFilmwork, Person, PersonFilmwork


class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmwork
    autocomplete_fields = ("genre", "film_work")


class PersonFilmworkInline(admin.TabularInline):
    model = PersonFilmwork
    autocomplete_fields = ("person", "film_work")


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    inlines = (GenreFilmworkInline,)
    list_display = ("title", "type", "creation_date", "rating", "created", "modified")
    list_filter = ("type",)
    search_fields = ("title",)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Person)
class Person(admin.ModelAdmin):
    list_display = ("full_name",)
    search_fields = ("film_work", "person")
    inlines = (PersonFilmworkInline,)
