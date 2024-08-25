import uuid

from django.contrib.auth.models import AbstractBaseUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from movies.custom_storage import CustomStorage

from .my_user_manager import MyUserManager


class FilmType(models.TextChoices):
    MOVIE = "movie", _("Movie")
    TV_SHOW = "tv_show", _("Tv show")


class RoleType(models.TextChoices):
    DIRECTOR = "director", _("Director")
    WRITER = "writer", _("Writer")
    ACTOR = "actor", _("Actor")


class Gender(models.TextChoices):
    MALE = "male", _("male")
    FEMALE = "female", _("female")


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(TimeStampedMixin, UUIDMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("name"), max_length=255)
    description = models.TextField(_("description"), blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'content"."genre'
        verbose_name = _("Genre")
        verbose_name_plural = _("Genres")

    def __str__(self):
        return self.name


class Filmwork(TimeStampedMixin, UUIDMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_("title"), max_length=255)
    description = models.TextField(_("description"), blank=True)
    creation_date = models.DateField(_("creation date"))
    rating = models.FloatField(
        _("rating"),
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    type = models.CharField(_("type"), choices=FilmType.choices, default=FilmType.MOVIE, max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    genres = models.ManyToManyField(Genre, through="GenreFilmwork")
    file = models.FileField(_("file"), storage=CustomStorage(), null=True)
    certificate = models.CharField(_("certificate"), max_length=512, blank=True)

    class Meta:
        db_table = 'content"."film_work'
        verbose_name = _("Filmwork")
        verbose_name_plural = _("Filmworks")
        indexes = [
            models.Index(fields=["creation_date"], name="film_work_creation_date_idx"),
        ]

    def __str__(self):
        return self.title


class GenreFilmwork(UUIDMixin):
    film_work = models.ForeignKey("Filmwork", on_delete=models.CASCADE)
    genre = models.ForeignKey("Genre", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'content"."genre_film_work'
        verbose_name = _("Genre filmwork")
        verbose_name_plural = _("Genres filmworks")
        indexes = [
            models.Index(fields=["film_work", "genre"], name="genre_film_work_genre_idx"),
        ]


class Person(TimeStampedMixin, UUIDMixin):
    full_name = models.CharField("full name", max_length=255)
    films = models.ManyToManyField(Filmwork, through="PersonFilmwork")
    gender = models.TextField(_("gender"), choices=Gender.choices, null=True)

    class Meta:
        db_table = 'content"."person'
        verbose_name = _("Person")
        verbose_name_plural = _("Persons")

    def __str__(self):
        return self.full_name


class PersonFilmwork(UUIDMixin):
    person = models.ForeignKey("Person", on_delete=models.CASCADE)
    film_work = models.ForeignKey("Filmwork", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    role = models.CharField(_("role"), choices=RoleType.choices, max_length=30, null=True)

    class Meta:
        db_table = 'content"."person_film_work'
        verbose_name = _("Person filmwork")
        verbose_name_plural = _("Persons filmworks")
        indexes = [
            models.Index(fields=["film_work", "person"], name="film_work_person_idx"),
        ]

    def __str__(self):
        return self.role


class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(verbose_name="email address", max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    # строка с именем поля модели, которая используется в качестве уникального идентификатора
    USERNAME_FIELD = "email"

    # менеджер модели
    objects = MyUserManager()

    def __str__(self):
        return f"{self.email} {self.id}"

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
