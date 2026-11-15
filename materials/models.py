from django.conf import settings
from django.db import models


class Course(models.Model):
    """Описывает модель Курс"""

    name = models.CharField(max_length=150, verbose_name="Курс", unique=True, help_text="Название курса")
    preview = models.ImageField(
        upload_to="materials/courses/preview",
        null=True,
        blank=True,
        verbose_name="Превью курса",
        help_text="Загрузите изображение (необязательно)",
    )
    description = models.TextField(null=True, blank=True, verbose_name="Описание курса", help_text="Описание курса")
    owner = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Владелец",
        related_name="courses",
        help_text="Владелец курса",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата последнего изменения")


class Lesson(models.Model):
    """Описывает модель урок"""

    name = models.CharField(max_length=150, verbose_name="Урок", unique=True, help_text="Название урока")
    description = models.TextField(null=True, blank=True, verbose_name="Описание урока", help_text="Описание урока")
    course = models.ForeignKey(
        to=Course, on_delete=models.SET_NULL, related_name="lessons", null=True, blank=True, verbose_name="Курс"
    )
    preview = models.ImageField(
        upload_to="materials/lessons/preview",
        null=True,
        blank=True,
        verbose_name="Превью курса",
        help_text="Загрузите изображение (необязательно)",
    )
    link = models.CharField(
        max_length=200, verbose_name="Ссылка на урок", null=True, blank=True, help_text="Ссылка на урок"
    )
    owner = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Владелец",
        related_name="lessons",
        help_text="Владелец урока",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата последнего изменения")
