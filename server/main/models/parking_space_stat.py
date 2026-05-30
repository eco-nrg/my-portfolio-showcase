import uuid

from django.db import models

from main.models.parking_space import ParkingSpace


class ParkingSpaceStat(models.Model):
    # Relationship Fields
    space = models.ForeignKey(
        'main.ParkingSpace',
        on_delete=models.CASCADE,
        related_name='stats',
        verbose_name='Парковочное место',
    )

    # Fields
    uuid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    status = models.CharField(
        max_length=5,
        choices=ParkingSpace.STATUS_CHOICES,
        verbose_name='Статус',
    )
    total_kw = models.DecimalField(
        max_digits=19,
        decimal_places=3,
        verbose_name='Накопленная энергия',
    )
    current_w = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Текущее значение мощности',
    )
    current_v = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Текущее значение напряжения',
    )
    current_a = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Текущее значение тока',
    )
    is_on = models.BooleanField(
        default=False,
        verbose_name='Счетчик включен',
    )
    is_occupied = models.BooleanField(
        default=False,
        verbose_name='Парковка занята машиной',
    )
    last_data_update = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Статистика места'
        verbose_name_plural = 'Статистика мест'

    def __str__(self):
        return f'{self.space.name} - {self.created_at}'
