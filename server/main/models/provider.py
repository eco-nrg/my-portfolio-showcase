from django.db import models


class Provider(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Общество с ограниченной ответственностью',
    )
    address = models.CharField(
        verbose_name='Юридический и фактический адрес',
        blank=True,
    )
    ogrn = models.CharField(
        max_length=16,
        verbose_name='ОГРН',
        blank=True,
    )
    inn = models.CharField(
        max_length=16,
        verbose_name='ИНН',
        blank=True,
    )
    kpp = models.CharField(
        max_length=16,
        verbose_name='КПП',
        blank=True,
    )
    payment_account = models.CharField(
        max_length=32,
        verbose_name='Расчетный счет',
        blank=True,
    )
    branch_office = models.CharField(
        max_length=64,
        verbose_name='Филиал',
        blank=True,
    )
    pao = models.CharField(verbose_name='ПАО', blank=True)
    bik = models.CharField(max_length=16, verbose_name='БИК', blank=True)
    correspondent_account = models.CharField(
        verbose_name='Корреспондентский счет',
        blank=True,
    )
    extra_information = models.JSONField(
        verbose_name='Дополнительная информация по провайдеру',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Провайдер'
        verbose_name_plural = 'Провайдеры'

    def __str__(self):
        return self.name
