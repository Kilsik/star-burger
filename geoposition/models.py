from django.db import models
from django.utils import timezone


class Location(models.Model):
    address = models.CharField(
        'адрес',
        max_length=300,
        db_index=True,
        unique=True,
    )
    latitude = models.FloatField(
        'широта',
        blank=True,
        null=True,
    )
    longitude = models.FloatField(
        'долгота',
        blank=True,
        null=True,
    )
    updated_at = models.DateTimeField(
        'дата и время обновления геопозиции',
        default=timezone.now,
    )

    class Meta:
        verbose_name = 'Локация'
        verbose_name_plural = 'Локации'
