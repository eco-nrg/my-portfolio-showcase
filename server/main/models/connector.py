from typing import TYPE_CHECKING

from django.db import models

if TYPE_CHECKING:
    from main.models import ParkingSpace  # noqa: F401


class ParkingSpaceConnector(models.Model):
    CONNECTOR_CHOICES = (
        ('IEC_62196', 'IEC 62196'),
        ('J1772', 'J1772'),
        ('TES_US', 'Tesla Us'),
        ('GB_T_AC', 'GB/T (AC)'),
    )
    CONNECTOR_IMAGES = (
        ('IEC_62196', '/static/connector/iec_62196.png'),
        ('J1772', '/static/connector/j1772.png'),
        ('TES_US', '/static/connector/tesla_us.png'),
        ('GB_T_AC', '/static/connector/gb_t_ac.png'),
    )
    # Relationship Fields
    space = models.ForeignKey['ParkingSpace'](
        'main.ParkingSpace',
        on_delete=models.CASCADE,
        related_name='connectors',
        verbose_name='Парковочное место',
    )

    # Fields
    connector_type = models.CharField(
        max_length=20,
        choices=CONNECTOR_CHOICES,
        verbose_name='Тип разъема',
    )
    phases_count = models.SmallIntegerField(verbose_name='Кол-во фаз')
    max_kw = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Максимальная мощность, кВт',
    )
    max_a = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Максимальный ток, А',
    )
    relay_pin_number = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Пин реле',
    )

    class Meta:
        ordering = ('-pk',)
        verbose_name = 'Коннектор места'
        verbose_name_plural = 'Коннекторы мест'

    def __str__(self):
        return f'{self.connector_type} {self.phases_count} {self.max_a}'
