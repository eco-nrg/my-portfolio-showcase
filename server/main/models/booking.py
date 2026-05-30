import uuid
from datetime import timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

from django.conf import settings
from django.db import models
from django.db.models import Case, F, Q, Value, When
from django.db.models.functions import Coalesce, Least, Now
from django.utils import timezone

from main.models.parking_space import SPACE_STATUSES

if TYPE_CHECKING:
    from django.contrib.auth.models import User  # noqa: F401

    from main.models import Order, ParkingSpace, ParkingSpaceConnector  # noqa: F401


class BookingStatus:
    # бронь была отменена автоматически или вручную пользователем
    CANCELLED = "CANCELLED"

    # бронь активировали, значит order_id ссылкается на реальную сессию зарядки
    ACTIVATED = "ACTIVATED"

    # невозможно, так как мы запрещаем бронировать в будущем, но вдруг...
    PLANNED = "PLANNED"

    # индикатор, что бронь должна быть немедленно завершена
    OVERDUE = "OVERDUE"

    # Бронь ждем пользователя бесплатно
    ACTIVE_FREE = "ACTIVE_FREE"

    # Бронь ждем пользователя платно
    ACTIVE_PAID = "ACTIVE_PAID"


# TODO: непонятно почему, но manager не работает в тестах
class BookingManager(models.Manager["Booking"]):
    def get_queryset(self):
        actual_duration = Coalesce(
            "activated_at",
            "cancelled_at",
            Least("booked_until", Now()),
        ) - F("created_at")

        status = Case(
            When(
                cancelled_at__isnull=False,
                then=Value(BookingStatus.CANCELLED),
            ),
            When(
                activated_at__isnull=False,
                then=Value(BookingStatus.ACTIVATED),
            ),
            When(
                created_at__gt=Now(),
                then=Value(BookingStatus.PLANNED),
            ),
            When(
                booked_until__lt=Now(),
                then=Value(BookingStatus.OVERDUE),
            ),
            When(
                cost__gt=Decimal(0),
                then=Value(BookingStatus.ACTIVE_PAID)
            ),
            default=Value(BookingStatus.ACTIVE_FREE),
        )

        return (
            super()
            .get_queryset()
            .annotate(
                _actual_duration=actual_duration,
                _status=status,
                _is_active=(
                    Q(_status__exact=BookingStatus.ACTIVE_FREE)
                    | Q(_status__exact=BookingStatus.ACTIVE_PAID)
                    | Q(_status__exact=BookingStatus.OVERDUE)
                ),
            )
        )


class Booking(models.Model):
    user = models.ForeignKey["User"](
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings",
        verbose_name="Пользователь",
    )
    uuid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    space = models.ForeignKey["ParkingSpace"](
        "main.ParkingSpace",
        on_delete=models.CASCADE,
        related_name="bookings",
        verbose_name="Парковочное место",
    )
    created_at = models.DateTimeField(
        verbose_name="Время создания",
    )
    booked_until = models.DateTimeField(
        verbose_name="Забронировано до",
    )
    activated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Время активации",
    )
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Время отмены",
    )
    order = models.OneToOneField["Order"](
        "main.Order",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="booking",
        verbose_name="Активированный заказ",
    )
    connector = models.ForeignKey["ParkingSpaceConnector"](
        "main.ParkingSpaceConnector",
        on_delete=models.CASCADE,
        related_name="bookings",
        verbose_name="Выбранный коннектор",
    )
    cost = models.DecimalField(
        default=Decimal(0),
        max_digits=19,
        decimal_places=2,
        verbose_name="Стоимость бронирования",
    )

    objects = BookingManager()

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"

    def __str__(self):
        return str(self.uuid)

    @property
    def is_active(self):
        # Бронирование считается активным, если оно просрочено,
        # так как понятие "OVERDUE" это внутренний маркер статуса брони
        # обозначающий, что бронирование вот-вот сервис отменит
        # но еще не отменил.
        return (
            self.status == BookingStatus.ACTIVE_FREE or
            self.status == BookingStatus.ACTIVE_PAID or
            self.status == BookingStatus.OVERDUE
        )

    @property
    def actual_duration(self) -> timedelta:
        date = (
            self.activated_at
            or self.cancelled_at
            or min(self.booked_until, timezone.now())
        )
        dt = date - self.created_at
        return timedelta(seconds=int(dt.total_seconds()))

    @property
    def left_time(self) -> timedelta:
        date = (
            self.activated_at
            or self.cancelled_at
            or min(self.booked_until, timezone.now())
        )
        dt = self.booked_until - date
        return min(max(dt, timedelta(0)), timedelta(hours=1))

    @property
    def status(self):
        if self.cancelled_at is not None:
            return BookingStatus.CANCELLED
        if self.activated_at is not None:
            return BookingStatus.ACTIVATED
        if self.created_at >= timezone.now():
            return BookingStatus.PLANNED
        if self.booked_until <= timezone.now():
            return BookingStatus.OVERDUE
        if self.cost > Decimal(0):
            return BookingStatus.ACTIVE_PAID
        return BookingStatus.ACTIVE_FREE

    def cancel(self):
        if self.is_active:
            self.cancelled_at = timezone.now()
            self.save(update_fields=["cancelled_at"])
            if self.space.status == SPACE_STATUSES.BOOKED:
                self.space.status = SPACE_STATUSES.AVAILABLE
                self.space.save(update_fields=["status"])
