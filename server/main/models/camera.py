import os
from typing import TYPE_CHECKING

from django.db import models
from django.utils.safestring import mark_safe

if TYPE_CHECKING:
    from main.models import ParkingLot, ParkingSpace  # noqa: F401


def get_image_path(instance: 'Camera', filename: str) -> str:
    ext = filename.split('.')[-1]
    return os.path.join(
        'camera',
        f'image_{instance.id}',
        f'{instance.image_iter}.{ext}',
    )


class Camera(models.Model):
    # Relationship Fields
    lot = models.ForeignKey['ParkingLot'](
        'main.ParkingLot',
        on_delete=models.CASCADE,
        related_name='cameras',
        verbose_name='Парковка',
    )
    space = models.ForeignKey['ParkingSpace'](
        'main.ParkingSpace',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Парковочное место',
        related_name='cameras',
    )
    send_by_space = models.ForeignKey['ParkingSpace'](
        'main.ParkingSpace',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Отправлять общий вид с этого устройства',
        related_name='send_space_cameras',
    )

    # Fields
    name = models.CharField(max_length=255, verbose_name='Название')
    ip = models.CharField(max_length=15, verbose_name='IP адрес')
    rtsp_url = models.CharField(
        max_length=255,
        verbose_name='RTSP URL',
        help_text='Полный URL подключения',
    )
    image = models.ImageField(upload_to=get_image_path)
    image_iter = models.SmallIntegerField(default=0)
    last_image_update = models.DateTimeField(auto_now_add=True)
    order_index = models.IntegerField(verbose_name='Индекс сортировки')

    class Meta:
        ordering = ('-order_index',)
        verbose_name = 'Камера'
        verbose_name_plural = 'Камеры'

    def __str__(self):
        return f'{self.name}'

    def save(self, *args, **kwargs):
        if self.send_by_space is not None and self.space is not None:
            raise ValueError('Select only lot camera or space camera')

        if self.space is not None and self.space.lot.id != self.lot.id:
            raise ValueError("Lot space don't match space")
        super().save(*args, **kwargs)

    @property
    def img_preview(self):
        return mark_safe(f'<img src = "{self.image.url}" width = "300"/>')  # noqa: S308
