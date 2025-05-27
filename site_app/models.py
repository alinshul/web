# import datetime
# from django.contrib.auth.models import AbstractUser
# from django.core.validators import RegexValidator
# from django.utils.translation import gettext_lazy as _
# from django.db import models
# from django.contrib.contenttypes.models import ContentType
# from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
# from django.conf import settings
#
#
# class CustomUser(AbstractUser):
#     phone = models.CharField(max_length=20, blank=True)
#     telegram_id = models.BigIntegerField(null=True, blank=True, unique=True)
#     is_telegram_user = models.BooleanField(default=False)
#
#
# class Feedback(models.Model):
#     SOURCE_CHOICES = [
#         ('WEB', 'Веб-сайт'),
#         ('TG', 'Telegram'),
#     ]
#
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     message = models.TextField()
#     source = models.CharField(max_length=3, choices=SOURCE_CHOICES)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return f"Отзыв от {self.user.username} ({self.get_source_display()})"
#
#
# class Reservation(models.Model):
#     class Status(models.TextChoices):
#         PENDING = 'pending', _('Ожидает подтверждения')
#         CONFIRMED = 'confirmed', _('Подтверждено')
#         CANCELLED = 'cancelled', _('Отменено')
#         COMPLETED = 'completed', _('Завершено')
#
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name='reservations',
#         verbose_name='Пользователь'
#     )
#     date = models.DateField(verbose_name='Дата бронирования')
#     time = models.TimeField(verbose_name='Время бронирования')
#     persons = models.PositiveSmallIntegerField(
#         default=2,
#         verbose_name='Количество персон'
#     )
#     status = models.CharField(
#         max_length=10,
#         choices=Status.choices,
#         default=Status.PENDING,
#         verbose_name='Статус'
#     )
#     created_at = models.DateTimeField(
#         auto_now_add=True,
#         verbose_name='Дата создания'
#     )
#     updated_at = models.DateTimeField(
#         auto_now=True,
#         verbose_name='Дата обновления'
#     )
#     comment = models.TextField(
#         blank=True,
#         verbose_name='Комментарий'
#     )
#
#     class Meta:
#         verbose_name = 'Бронирование'
#         verbose_name_plural = 'Бронирования'
#         ordering = ['date', 'time']
#         constraints = [
#             models.UniqueConstraint(
#                 fields=['date', 'time', 'user'],
#                 name='unique_user_reservation'
#             )
#         ]
#
#     def __str__(self):
#         return (
#             f"Бронирование #{self.id} на {self.date} "
#             f"в {self.time.strftime('%H:%M')} "
#             f"({self.get_status_display()})"
#         )
#
#     @property
#     def datetime(self):
#         return datetime.combine(self.date, self.time)
#
#     likes_dislikes = GenericRelation('LikeDislike')
#
#
# class Comment(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     text = models.TextField()
#     content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
#     object_id = models.PositiveIntegerField()
#     content_object = GenericForeignKey('content_type', 'object_id')
#     created_at = models.DateTimeField(auto_now_add=True)
#
#
# class LikeDislike(models.Model):
#     LIKE = 1
#     DISLIKE = -1
#     VOTE_CHOICES = ((LIKE, 'Like'), (DISLIKE, 'Dislike'))
#
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     vote = models.SmallIntegerField(choices=VOTE_CHOICES)
#     content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
#     object_id = models.PositiveIntegerField()
#     content_object = GenericForeignKey('content_type', 'object_id')
#
#     class Meta:
#         unique_together = ('user', 'content_type', 'object_id')


import datetime
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=20, blank=True)
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True)
    is_telegram_user = models.BooleanField(default=False)

class Feedback(models.Model):
    SOURCE_CHOICES = [
        ('WEB', 'Веб-сайт'),
        ('TG', 'Telegram'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    source = models.CharField(max_length=3, choices=SOURCE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Отзыв от {self.user.username} ({self.get_source_display()})"

class Reservation(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', _('Ожидает подтверждения')
        CONFIRMED = 'confirmed', _('Подтверждено')
        CANCELLED = 'cancelled', _('Отменено')
        COMPLETED = 'completed', _('Завершено')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name='Пользователь'
    )
    date = models.DateField(verbose_name='Дата бронирования')
    time = models.TimeField(verbose_name='Время бронирования')
    persons = models.PositiveSmallIntegerField(
        default=2,
        verbose_name='Количество персон'
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Статус'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    comment = models.TextField(
        blank=True,
        verbose_name='Комментарий'
    )
    likes_dislikes = GenericRelation('LikeDislike')

    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'
        ordering = ['date', 'time']
        constraints = [
            models.UniqueConstraint(
                fields=['date', 'time', 'user'],
                name='unique_user_reservation'
            )
        ]

    # def __str__(self):
    #     return (
    #         f"Бронирование #{self.id} на {self.date} "
    #         f"в {self.time.strftime('%H:%M')} "
    #         f"({self.get_status_display()})"
    #     )

    def __str__(self):
        return self.comment if self.comment else f"Бронирование #{self.id}"

    @property
    def datetime(self):
        return datetime.datetime.combine(self.date, self.time)


    # @property
    # def likes_count(self):
    #     """Количество лайков для этого бронирования"""
    #     return self.likes_dislikes.filter(vote=LikeDislike.LIKE).count()
    #
    # @property
    # def dislikes_count(self):
    #     """Количество дизлайков для этого бронирования"""
    #     return self.likes_dislikes.filter(vote=LikeDislike.DISLIKE).count()


# class Comment(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     text = models.TextField()
#     content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
#     object_id = models.PositiveIntegerField()
#     content_object = GenericForeignKey('content_type', 'object_id')
#     created_at = models.DateTimeField(auto_now_add=True)

    #
    #
    # class Meta:
    #     ordering = ['-created_at']

class LikeDislike(models.Model):
    LIKE = 1
    DISLIKE = -1
    VOTE_CHOICES = (
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike')
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vote = models.SmallIntegerField(choices=VOTE_CHOICES)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]