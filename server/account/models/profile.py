from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Case, DecimalField, F, Sum, Value, When
from django.db.models.signals import post_save

from payments.models import BonusOperationType, OperationType

DEFAULT_FREE_SECONDS: int = settings.DEFAULT_FREE_HOURS * 60 * 60


class Profile(models.Model):
    FAST_CHOICES = (
        ("CHADEMO", "CHADEMO"),
        ("CCS-Combo1", "CCS-Combo1"),
        ("CCS-Combo2", "CCS-Combo2"),
        ("GB-T", "GB-T"),
    )
    SLOW_CHOICES = (
        ("J1772", "TYPE1 (J1772)"),
        ("IEC62196", "TYPE2 (IEC62196)"),
        ("TESLA_US", "TESLA US"),
        ("GB_T_AC", "GB/T (AC)"),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="profile",
        on_delete=models.CASCADE,
    )
    email = models.EmailField("Электронная почта", null=True, blank=True)
    first_name = models.CharField("Имя", max_length=50, blank=True)
    middle_name = models.CharField("Отчество", max_length=50, blank=True)
    car_manufacturer = models.CharField(
        "Марка машины",
        max_length=50,
        blank=True,
    )
    car_model = models.CharField("Модель машин", max_length=50, blank=True)
    car_number = models.CharField("Номер машины", max_length=20, blank=True)
    car_year = models.PositiveSmallIntegerField(
        "Год выпуска",
        null=True,
        blank=True,
    )
    battery_power = models.DecimalField(
        "Емкость батареи",
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
    )
    fast_type = models.CharField(
        "Быстрый тип",
        max_length=15,
        choices=FAST_CHOICES,
        blank=True,
        null=True,
    )
    slow_type = models.CharField(
        "Медленный тип",
        max_length=15,
        choices=SLOW_CHOICES,
        blank=True,
        null=True,
    )
    rating = models.PositiveIntegerField("Рейтинг", default=0)
    can_charge_free = models.BooleanField(
        "Может заряжаться бесплатно",
        default=True,
    )
    can_book = models.BooleanField("Может бронировать", default=True)
    free_seconds = models.PositiveIntegerField(
        "Бесплатных секунд",
        default=DEFAULT_FREE_SECONDS,
    )
    is_filled = models.BooleanField(
        default=False,
        verbose_name="Профиль заполнен",
    )
    code = models.CharField("Код входа", max_length=6, default="000000")
    last_code_sent = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField("Сохранен", auto_now_add=True)
    trial_time = models.PositiveBigIntegerField(
        "Бесплатное время зарядки",
        default=0,
    )

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return f"Profile for {self.user.username}"

    def save(self, *args, **kwargs):
        self.is_filled = all(
            [
                self.email,
                self.first_name,
                self.middle_name,
                self.car_manufacturer,
                self.car_model,
                self.car_number,
                self.car_year,
                self.battery_power,
                self.fast_type,
                self.slow_type,
            ],
        )
        super().save(*args, **kwargs)

    @property
    def balance(self):
        """Вычисляет баланс аккаунта.

        Вычисляемое поле, запрашивать его для списка пользователей долго.
        Если понадобится часто это делать - нужно заменить на настоящее поле.
        """
        return (
            self.user.operations.aggregate(
                balance=Sum(
                    Case(
                        When(kind=OperationType.DEBIT, then=F("amount")),
                        When(kind=OperationType.CREDIT, then=-F("amount")),
                        default=Value(0),
                        output_field=DecimalField(),
                    ),
                ),
            )["balance"]
            or 0
        )

    @property
    def bonus_balance(self):
        """Баланс бонусов пользователя.

        Вычисляемое поле, запрашивать его для списка пользователей долго.
        Если понадобится часто это делать - нужно заменить на настоящее поле
        """
        return (
            self.user.bonus_operations.aggregate(
                bonus_balance=Sum(
                    Case(
                        When(kind=BonusOperationType.DEBIT, then=F("amount")),
                        When(kind=BonusOperationType.CREDIT, then=-F("amount")),
                        default=Value(0),
                        output_field=DecimalField(),
                    ),
                ),
            )["bonus_balance"]
            or 0
        )

    def reset_limits(self):
        self.can_book = True
        self.free_seconds = DEFAULT_FREE_SECONDS
        self.save(update_fields=["free_seconds", "can_book"])


def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


post_save.connect(create_profile, sender=User)
