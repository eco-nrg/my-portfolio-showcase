import binascii
import os
from typing import TYPE_CHECKING

from django.db import models

if TYPE_CHECKING:
    from main.models import ParkingLot, ParkingSpace  # noqa: F401

DEVICE_KEY_LEN = 20


def generate_key() -> str:
    return binascii.hexlify(os.urandom(DEVICE_KEY_LEN)).decode()


class Device(models.Model):
    # Relationship Fields
    lot = models.ForeignKey['ParkingLot'](
        'main.ParkingLot',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='devices',
        verbose_name='Парковка',
    )
    space = models.ForeignKey['ParkingSpace'](
        'main.ParkingSpace',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='devices',
        verbose_name='Место',
    )

    # Fields
    name = models.CharField('Название', max_length=255)
    key = models.CharField('Ключ', max_length=40, primary_key=True)

    class Meta:
        verbose_name = 'Устройство'
        verbose_name_plural = 'Устройства'

    def __str__(self):
        return f'{self.key} {self.name}'

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = generate_key()

        if self.lot and self.space:
            raise ValueError('Set only space or lot')
        elif self.space:
            count = self.space.devices.count()
            if count > 1 or (count == 1 and self.space.devices.first().pk != self.pk):
                msg = f'Multiple devices at space {self.space.uid}'
                raise ValueError(msg)
        elif self.lot:
            count = self.lot.devices.count()
            if count > 1 or (count == 1 and self.lot.devices.first().pk != self.pk):
                msg = f'Multiple devices at lot {self.space.uid}'
                raise ValueError(msg)

        return super().save(*args, **kwargs)
