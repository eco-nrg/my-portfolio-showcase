import uuid
from datetime import timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

import structlog
from django.conf import settings
from django.db import models, transaction
from django.db.models import F, Q
from django.db.models.functions import Coalesce, Extract, Now
from django.utils import timezone

from main.models.parking_space import SPACE_MODES, SPACE_STATUSES
from payments.models import Operation, OperationAction, OperationType

if TYPE_CHECKING:
    from django.contrib.auth.models import User  # noqa: F401

    from main.models import Camera  # noqa: F401
    from main.models import ParkingSpace  # noqa: F401
    from main.models import ParkingSpaceConnector  # noqa: F401

logger = structlog.get_logger(__name__)

SECONDS_TO_HOURS = 3600


class ORDER_STATUSES:
    ACTIVE = "ACT"
    NO_MONEY = "NOM"
    FINISHED = "FIN"
    PARKING = "PAR"
    FINISHED_PARKING = "FPR"


class OrderManager(models.Manager["Order"]):
    def get_queryset(self):
        # Считаем на базе данных делту времени между началом Заказа и
        # концом или текущим временм.
        # EXTRACT(EPOCH FROM (COALESCE(finished_at, now()) - created_at)) as dt
        duration = Extract(
            Coalesce("finished_at", Now()) - F("created_at"),
            lookup_name="EPOCH",
        )
        delta_kw = Coalesce("end_kw", "last_kw", "start_kw") - F("start_kw")
        return (
            super()
            .get_queryset()
            .annotate(
                _duration=duration,
            )
            .annotate(
                _delta_kw=delta_kw,
            )
            .annotate(
                _is_active=Q(status=ORDER_STATUSES.ACTIVE),
            )
        )


class Order(models.Model):
    STATUS_CHOICES = (
        (ORDER_STATUSES.ACTIVE, "Активен"),
        (ORDER_STATUSES.NO_MONEY, "Без оплаты"),
        (ORDER_STATUSES.FINISHED, "Завершен"),
        (ORDER_STATUSES.PARKING, "Простой"),
        (ORDER_STATUSES.FINISHED_PARKING, "Простой завершен"),
    )
    # Relationship Fields
    user = models.ForeignKey["User"](
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Пользователь",
    )
    space = models.ForeignKey["ParkingSpace"](
        "main.ParkingSpace",
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Парковочное место",
    )
    connector_type = models.ForeignKey["ParkingSpaceConnector"](
        "main.ParkingSpaceConnector",
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Выбранный коннектор",
    )
    selected_camera = models.ForeignKey["Camera"](
        "main.Camera",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Выбранная камера",
    )

    # Fields
    uuid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    status = models.CharField(
        max_length=5,
        choices=STATUS_CHOICES,
        verbose_name="Статус",
    )
    start_kw = models.DecimalField(
        max_digits=19,
        decimal_places=3,
        verbose_name="Начальная накопленная энергия",
    )
    end_kw = models.DecimalField(
        max_digits=19,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Конечная накопленная энергия",
    )
    last_kw = models.DecimalField(
        max_digits=19,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Последняя обработанная накопленная энергия",
    )
    last_process_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Время последней обработки",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    start_payed = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Время начала платной зарядки",
    )
    payed_seconds = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=Decimal(0),
        editable=False,
        verbose_name="Платное время",
    )
    payed_kw = models.DecimalField(
        max_digits=19,
        decimal_places=5,
        default=Decimal(0),
        editable=False,
        verbose_name="Платных киловатт",
    )
    finished_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Завершен",
    )

    cost_kw = models.DecimalField(
        default=Decimal(0),
        max_digits=19,
        decimal_places=2,
        verbose_name="Стоимость кВт",
    )
    cost_time = models.DecimalField(
        default=Decimal(0),
        max_digits=19,
        decimal_places=2,
        verbose_name="Стоимость за простой", # Обычный простой, не штрафной
    )
    cost_penalty = models.DecimalField(
        default=Decimal(0),
        max_digits=19,
        decimal_places=2,
        verbose_name="Двойной штраф за простой",
    )
    penalty_seconds = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=Decimal(0),
        editable=False,
        verbose_name="Время штрафного простоя",
    )

    objects = OrderManager()

    class Meta:
        ordering = ("-pk",)
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return str(self.uuid)

    @property
    def duration(self) -> int:
        return self._duration

    @property
    def duration_dt(self):
        return timedelta(seconds=self.duration)

    @property
    def delta_kw(self) -> Decimal:
        return self._delta_kw

    @property
    def can_charge_time(self):
        return self.space.mode == SPACE_MODES.TEST

    @property
    def can_charge_money(self):
        return self.space.mode == SPACE_MODES.PRODUCTION

    @property
    def cost_booking(self) -> Decimal:
        try:
            return self.booking.cost
        except Exception:
            return Decimal(0)

    @property
    def cost_total(self) -> Decimal:
        return self.cost_kw + self.cost_time + self.cost_penalty

    @property
    def cost_without_kw(self) -> Decimal:
        return self.cost_time + self.cost_penalty

    @property
    def cost_total_with_booking(self) -> Decimal:
        return self.cost_total + self.cost_booking

    # resolves to how long order has been active (processed)
    @property
    def processing_time(self):
        return self.last_process_time - self.created_at

    @transaction.atomic
    def finish(self, status: str):
        logger.info(
            "Finish order",
            order_id=str(self.uuid),
            space=self.space.uid,
            start_kw=float(self.start_kw),
            end_kw=float(self.space.total_kw),
            new_status=status,
            duration=self.duration,
            payed_seconds=self.payed_seconds,
            payed_kw=self.payed_kw,
            dt=(timezone.now() - self.created_at).total_seconds(),
        )

        if (
            self.status == ORDER_STATUSES.PARKING
            and status != ORDER_STATUSES.FINISHED_PARKING
        ):
            logger.error(
                "Invalid status transition",
                order_status=self.status,
                new_status=status,
            )
            return

        self.status = status
        self.end_kw = self.space.total_kw
        self.finished_at = timezone.now()

        self.space.status = SPACE_STATUSES.AVAILABLE

        self.user.profile.refresh_from_db()

        if self.can_charge_time:
            duration = (self.finished_at - self.created_at).total_seconds()
            self.user.profile.free_seconds -= int(duration)
            if self.user.profile.free_seconds < 0:
                self.user.profile.free_seconds = 0
            self.user.profile.save(update_fields=["free_seconds"])
        elif self.can_charge_money:
            if self.user.profile.trial_time != 0:
                self.user.profile.trial_time = 0
                self.user.profile.save(update_fields=["trial_time"])
                Operation.objects.create(
                    kind=OperationType.CREDIT,
                    action=OperationAction.ORDER,
                    amount=Decimal(0.01) + self.cost_without_kw,
                    created_at=self.finished_at,
                    user=self.user,
                    order=self,
                )
            else:
                Operation.objects.create(
                    kind=OperationType.CREDIT,
                    action=OperationAction.ORDER,
                    amount=self.cost_total,
                    created_at=self.finished_at,
                    user=self.user,
                    order=self,
                )
        else:
            logger.error(
                "Failed to charge: unknown space.mode",
                mode=self.space.mode,
                space=self.space.uid,
                order_id=str(self.uuid),
            )

        self.save(update_fields=["status", "end_kw", "finished_at"])
        self.space.save(update_fields=["status"])

    def finish_no_money(self):
        self.finish(ORDER_STATUSES.NO_MONEY)
