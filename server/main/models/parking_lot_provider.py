from django.db import models

from main.models.provider import Provider


class ProviderType:
    PROVIDING = 'PROVIDING'  # Организация предоставляющая услуги
    SERVICE = 'SERVICE'  # Обслуживающая организация


class ProviderParkingLot(models.Model):
    PROVIDER_TYPE = (
        ('PROVIDING', 'Организация предоставляющая услуги'),
        ('SERVICE', 'Обслуживающая организация'),
    )
    parking_lot = models.ForeignKey(
        'main.ParkingLot',
        on_delete=models.CASCADE,
        verbose_name='Парковка',
    )
    providers = models.ManyToManyField(
        Provider,
        related_name='parking_relationships',
        verbose_name='Провайдеры',
    )
    provider_type = models.CharField(
        max_length=20,
        choices=PROVIDER_TYPE,
        verbose_name='Тип провайдера',
    )

    class Meta:
        verbose_name = 'провайдера для парковочного места'
        verbose_name_plural = 'Провайдеры для парковочного места'
        unique_together = ('parking_lot', 'provider_type')

    def __str__(self):
        return f'{self.parking_lot} - {self.get_provider_type_declension()}'

    def get_provider_type_declension(self):
        # Define custom declensions based on the provider_type values
        declensions = {
            'PROVIDING': 'Организации предоставляющие услуги',
            'SERVICE': 'Обслуживающие организации',
        }
        return declensions.get(self.provider_type, '')
