from django.db import models


class TelegramUser(models.Model):
    """Модель пользователя из телеграма."""
    telegram_id = models.BigIntegerField(
        unique=True,
        blank=True,
        null=True,
        verbose_name='ID в телеграме',
    )
    username = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        verbose_name='username в телеграме',
    )

    class Meta:
        verbose_name = 'Пользователь телеграма'
        verbose_name_plural = 'Пользователи телеграма'

    def __str__(self):
        return f'{self.username}/{self.telegram_id}'


class Event(models.Model):
    """Модель мероприятия."""
    name = models.CharField(
        max_length=100,
        blank=False,
        null=False,
        verbose_name='Название',
    )
    location = models.URLField(
        blank=False,
        null=False,
        verbose_name='Локация (ссылка)',
    )
    host = models.ForeignKey(
        to=TelegramUser,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='hosted_events',
    )
    created_by = models.ForeignKey(
        to=TelegramUser,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='created_events',
    )

    class Meta:
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'

    def __str__(self):
        return self.name


class EventStatus(models.Model):
    """Модель статуса мероприятия."""
    event = models.ForeignKey(
        to=Event,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name='status',
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('CONFIRMED', 'Confirmed'),
            ('REJECTED', 'Rejected'),
        ],
        default='PENDING',
    )

    class Meta:
        verbose_name = 'Статус мероприятия'
        verbose_name_plural = 'Статусы мероприятий'

    def __str__(self):
        return f'{self.event.name} - {self.status}'
