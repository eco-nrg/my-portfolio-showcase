import os
from typing import TYPE_CHECKING

from django.db import models

if TYPE_CHECKING:
    from main.models import City  # noqa: F401


def get_map_path(instance: 'ParkingLot', filename: str) -> str:
    ext = filename.split('.')[-1]
    return os.path.join(
        'map',
        f'{str(instance.id)}.{ext}',
    )


class ParkingLot(models.Model):
    # Relationship Fields
    city = models.ForeignKey['City'](
        'main.City',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='lots',
        verbose_name='Город',
    )

    # Fields
    uid = models.CharField(max_length=50, verbose_name='UID', unique=True)
    name = models.CharField(max_length=255, verbose_name='Название')
    address = models.CharField(max_length=255, verbose_name='Адрес')

    latitude = models.DecimalField(
        max_digits=18,
        decimal_places=14,
        verbose_name='Широта',
        null=True,
        blank=True,
    )
    longitude = models.DecimalField(
        max_digits=18,
        decimal_places=14,
        verbose_name='Долгота',
        null=True,
        blank=True,
    )
    zoom = models.PositiveSmallIntegerField('Масштаб', default=15)
    map_image = models.ImageField(
        upload_to=get_map_path,
        default='map/1.jpg',
        help_text='300 x 400 px',
        verbose_name='Изобажение карты',
    )

    class Meta:
        ordering = ('-pk',)
        verbose_name = 'Заправка'
        verbose_name_plural = 'Заправки'

    def __str__(self):
        return f'{self.uid} {self.name}'
