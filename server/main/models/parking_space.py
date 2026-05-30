from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

import structlog
from django.db import models, transaction
from django.utils import timezone

if TYPE_CHECKING:
    from main.models import Booking
    from main.models import Order
    from main.models import ParkingLot  # noqa: F401

logger = structlog.get_logger(__name__)


class SPACE_STATUSES:
    AVAILABLE = "AV"
    CHARGING = "CH"
    BUSY = "BU"
    DISABLED = "DI"
    BOOKED = "BO"


class SPACE_MODES:
    PRODUCTION = "PROD"
    TEST = "TEST"


class METER_MODELS:
    M_234_ART_02_POR = "M_234_ART_02_POR"  # старый с реле и RS-485
    M_234_ARTM2_02_POBR_R = "M_234_ARTM2_02_POBR_R"  # новый с реле и RS-485
    M_206_PRNO = "M_206_PRNO"


class PARKLOCK_TYPES:
    TTLOCK = "ttlock"
    QH_COM_PARKINGLOCK = "qh.com.parkinglock"


class ParkingSpace(models.Model):
    TYPE_CHOICES = (
        ("TES_US", "Tesla USA"),
        ("TES_EU", "Tesla EU"),
    )
    METER_CHOICES = (
        (METER_MODELS.M_234_ART_02_POR, "Меркурий 234 ART-01 POR (старый)"),
        (METER_MODELS.M_234_ARTM2_02_POBR_R, "Меркурий 234 ARTM2-02 POBR.R"),
        (METER_MODELS.M_206_PRNO, "Меркурий 206 PRNO"),
    )
    STATUS_CHOICES = (
        (SPACE_STATUSES.AVAILABLE, "Свободно"),
        (SPACE_STATUSES.BUSY, "Занято"),
        (SPACE_STATUSES.CHARGING, "Заряжается"),
        (SPACE_STATUSES.DISABLED, "Отключено"),
        (SPACE_STATUSES.BOOKED, "Забронировано"),
    )
    MODE_CHOICES = (
        (SPACE_MODES.PRODUCTION, "Боевая"),
        (SPACE_MODES.TEST, "Тестовая"),
    )
    PARKLOCK_CHOICES = (
        (PARKLOCK_TYPES.QH_COM_PARKINGLOCK, "Новый qh.com.parkinglock"),
    )
    # PRICE_CHOICES = (
    #     (Decimal("16.00"), "Tesla US 16р. 1 Квт."),
    #     (Decimal("15.00"), "IEC 62196 15р. 1 Квт."),
    #     (Decimal("14.00"), "J1772 14р. 1 Квт."),
    #     (Decimal("15.00"), "GB/T (AC) 15р. 1 Квт."),
    # )

    # Relationship Fields
    lot = models.ForeignKey["ParkingLot"](
        "main.ParkingLot",
        on_delete=models.CASCADE,
        related_name="spaces",
        verbose_name="Парковка",
    )

    # Fields
    charge_type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        verbose_name="Тип",
    )
    name = models.CharField(max_length=255, verbose_name="Название")
    uid = models.CharField(max_length=50, verbose_name="UID", unique=True)
    position = models.IntegerField(verbose_name='Порядковый номер', default=0)
    price_kw = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена за кВт",
    )
    price_hour = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена за час стоянки",
    )
    status = models.CharField(
        max_length=5,
        choices=STATUS_CHOICES,
        verbose_name="Статус",
    )
    last_active_status = models.CharField(
        max_length=5,
        choices=STATUS_CHOICES,
        verbose_name="Последний активный статус",
        editable=False,
        default=SPACE_STATUSES.AVAILABLE,
    )
    total_kw = models.DecimalField(
        max_digits=19,
        decimal_places=3,
        default=Decimal(0),
        verbose_name="Накопленная энергия",
        editable=False,
    )
    current_w = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal(0),
        verbose_name="Текущее значение мощности",
        editable=False,
    )
    current_v = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal(0),
        verbose_name="Текущее значение напряжения",
        editable=False,
    )
    current_a = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal(0),
        verbose_name="Текущее значение тока",
        editable=False,
    )
    is_occupied = models.BooleanField(
        default=False,
        verbose_name="Парковка занята машиной",
    )
    is_reed_installed = models.BooleanField(
        default=True,
        verbose_name="Пистолет вставлен на место",
    )
    is_manually_disabled = models.BooleanField(
        default=False,
        verbose_name="Станция выключена администратором",
        editable=False,
    )
    mode = models.CharField(
        default=SPACE_MODES.TEST,
        max_length=10,
        choices=MODE_CHOICES,
        verbose_name="Режим работы",
    )
    idle_amperage_threshold = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal(15),
        verbose_name="Пороговое значение напряжения для начисления простоя",
    )

    last_data_update = models.DateTimeField(auto_now_add=True)

    reed_install_time = models.DateTimeField(
        default=timezone.now,
        verbose_name="Время, когда был вставлен пистолет",
    )

    red_pin_number = models.PositiveSmallIntegerField(
        verbose_name="Номер пина красного диода",
        null=True,
        blank=True,
    )
    green_pin_number = models.PositiveSmallIntegerField(
        verbose_name="Номер пина зеленого диода",
        null=True,
        blank=True,
    )
    blue_pin_number = models.PositiveSmallIntegerField(
        verbose_name="Номер пина синего диода",
        null=True,
        blank=True,
    )
    parklock_led_pin_number = models.PositiveSmallIntegerField(
        verbose_name="Номер пина диода парклока",
        null=True,
        blank=True,
    )
    parklock_status_pin_number = models.PositiveSmallIntegerField(
        verbose_name="Номер пина для получение статуса парклока",
        null=True,
        blank=True,
    )
    park_lock_open_pin_number = models.PositiveSmallIntegerField(
        verbose_name="Номер пина для открытия парклока",
        null=True,
        blank=True,
    )
    park_lock_close_pin_number = models.PositiveSmallIntegerField(
        verbose_name="Номер пина для закрытия парклока",
        null=True,
        blank=True,
    )
    park_lock_serial_number = models.CharField(
        verbose_name="Серийный номер парклока",
        null=True,
        blank=True,
    )
    sonic_led_pin_number = models.PositiveSmallIntegerField(
        verbose_name="Номер пина диода парктроника",
        null=True,
        blank=True,
    )
    sonic_trigger_pin_number = models.PositiveSmallIntegerField(
        verbose_name="Номер пина триггера парктроника",
        null=True,
        blank=True,
    )
    sonic_echo_pin_number = models.PositiveSmallIntegerField(
        verbose_name="Номер пина эхо парктроника",
        null=True,
        blank=True,
    )
    reed_switch_pin_number = models.PositiveSmallIntegerField(
        verbose_name="Номер пина геркона",
        null=True,
        blank=True,
    )
    active_amp = models.PositiveSmallIntegerField(
        verbose_name="Уровень тока активной зарядки",
        help_text="Ампер",
        default=12,
    )
    sonic_floor_distance = models.FloatField(
        default=250,
        verbose_name="Расстояние до земли",
    )
    sonic_car_distance = models.FloatField(
        default=100,
        verbose_name="Расстояние до машины",
    )

    parklock_type = models.CharField(
        max_length=255,
        choices=PARKLOCK_CHOICES,
        default=PARKLOCK_TYPES.TTLOCK,
        verbose_name="Тип парклока",
    )
    parklock_mac = models.CharField(
        max_length=17,
        null=True,
        blank=True,
        verbose_name="MAC адрес парклока",
    )
    parklock_com_port = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="COM порт парклока",
    )

    meter_com_port = models.CharField(
        max_length=40,
        verbose_name="COM порт счетчика",
    )
    meter_code = models.PositiveIntegerField(
        verbose_name="Серийный номер счетчика",
        help_text="Код авторизации",
    )
    meter_model = models.CharField(
        max_length=255,
        choices=METER_CHOICES,
        default=METER_MODELS.M_234_ART_02_POR,
        verbose_name="Модель счетчика",
    )

    class Meta:
        ordering = ("-pk",)
        verbose_name = "Место"
        verbose_name_plural = "Места"

    def __str__(self) -> str:
        return f"{self.uid} {self.name}"

    @property
    def is_disabled(self) -> bool:
        return self.status == SPACE_STATUSES.DISABLED

    @property
    def is_on(self) -> bool:
        return self.status == SPACE_STATUSES.CHARGING

    @transaction.atomic
    def disable(self, manually: bool = False) -> None:
        logger.info(
            "disable",
            space_uid=self.uid,
            status=self.status,
            manually=manually,
        )
        self.is_manually_disabled = manually
        if self.status != SPACE_STATUSES.DISABLED:
            self.last_active_status = self.status
        self.status = SPACE_STATUSES.DISABLED
        self.save(
            update_fields=[
                "is_manually_disabled",
                "last_active_status",
                "status",
            ]
        )

    @transaction.atomic
    def enable(self, manually: bool = True) -> None:
        if self.is_manually_disabled and not manually:
            return

        logger.info(
            "enable",
            space_uid=self.uid,
            last_active_status=self.last_active_status,
            manually=manually,
        )
        self.is_manually_disabled = False
        self.status = self.last_active_status
        self.save(
            update_fields=[
                "is_manually_disabled",
                "status"
            ]
        )

    @property
    def get_price_kw(self) -> Decimal:
        if self.mode == SPACE_MODES.TEST:
            return Decimal(0)
        return self.price_kw

    @property
    def get_price_hour(self) -> Decimal:
        if self.mode == SPACE_MODES.TEST:
            return Decimal(0)
        return self.price_hour

    @property
    def is_booked(self) -> bool:
        return self.bookings.filter(
            _is_active=True,
        ).count() > 0

    @property
    def booking(self) -> Optional["Booking"]:
        return (
            self.bookings.filter(
                _is_active=True,
            )
            .order_by("-created_at")
            .first()
        )

    @property
    def order(self) -> Optional["Order"]:
        return self.orders.filter(
            _is_active=True,
        ).first()

    @property
    def booked_until(self) -> Optional["datetime"]:
        booking = self.booking
        if booking is None:
            return None
        return booking.booked_until
