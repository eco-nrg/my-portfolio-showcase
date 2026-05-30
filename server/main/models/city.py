from django.db import models
from pytils.translit import slugify


class City(models.Model):
    # Fields
    name = models.CharField(max_length=255, verbose_name='Название')
    slug = models.SlugField(unique=True, editable=False)

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
    map_zoom = models.PositiveSmallIntegerField('Масштаб', default=15)

    class Meta:
        ordering = ('pk',)
        verbose_name = 'Город'
        verbose_name_plural = 'Города'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def location(self):
        if self.latitude is not None and self.longitude is not None:
            return float(self.latitude), float(self.longitude)
        return None
