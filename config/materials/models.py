from django.db import models
from django.conf import settings
from .validators import validate_youtube_url


class Course(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название')
    preview = models.ImageField(upload_to='courses/previews/', verbose_name='Превью', null=True, blank=True)
    description = models.TextField(verbose_name='Описание', null=True, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'

    def __str__(self):
        return self.title

class Lesson(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(verbose_name='Описание', null=True, blank=True)
    preview = models.ImageField(upload_to='lessons/previews/', verbose_name='Превью', null=True, blank=True)
    video_link = models.URLField(
        verbose_name='Ссылка на видео',
        null=True,
        blank=True,
        validators=[validate_youtube_url]
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons', verbose_name='Курс')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'

    def __str__(self):
        return self.title


class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')
