from django import forms
from django.conf import settings
from django.contrib import admin
from django.db.models.fields.json import JSONField
from django.http import HttpResponseRedirect
from jsoneditor.forms import JSONEditor

from chat.event.booking import send_cancel_bookings
from chat.event.phone_auth import send_phone_auth_response
from chat.event.refill import send_refills
from chat.event.session import send_session_stop, send_sessions_history
from main.models import (
    ORDER_STATUSES,
    Booking,
    Camera,
    City,
    Device,
    Order,
    ParkingLot,
    ParkingSpace,
    ParkingSpaceConnector,
    ParkingSpaceStat,
    SmsSend,
)
from main.models.parking_lot_provider import ProviderParkingLot
from main.models.provider import Provider


def finish_order(modeladmin, request, queryset):
    for order in queryset:
        order.finish(ORDER_STATUSES.FINISHED)
        send_session_stop(order.user, space_id=order.space.id)
        send_phone_auth_response(order.user, order.user)
        send_sessions_history(order.user, order.user)
    send_refills('all')


finish_order.short_description = 'Завершить заказ'


# City
class CityAdminForm(forms.ModelForm):
    class Meta:
        model = City
        fields = '__all__'


class CityAdmin(admin.ModelAdmin):
    form = CityAdminForm
    list_display = ('name', 'slug')
    search_fields = ['name']


admin.site.register(City, CityAdmin)


# ParkingLot
class CameraInline(admin.TabularInline):
    model = Camera


class ParkingLotAdminForm(forms.ModelForm):
    class Meta:
        model = ParkingLot
        fields = '__all__'


class ParkingLotAdmin(admin.ModelAdmin):
    form = ParkingLotAdminForm
    inlines = [CameraInline]
    list_display = ('uid', 'name', 'address')
    search_fields = ['uid', 'name']


admin.site.register(ParkingLot, ParkingLotAdmin)


# ParkingSpace
class ParkingSpaceConnectorInline(admin.TabularInline):
    model = ParkingSpaceConnector


class ParkingSpaceAdminForm(forms.ModelForm):
    class Meta:
        model = ParkingSpace
        fields = '__all__'


def disable_station(modeladmin, request, queryset):
    for parking_space in queryset:
        if parking_space.order is not None:
            # Если на парковке выполняется заказ - не выключаем ее
            continue
        parking_space.disable(True)


disable_station.short_description = (
    'Выключить станцию (если она не используется сейчас)'
)


def enable_station(modeladmin, request, queryset):
    for parking_space in queryset:
        parking_space.enable(True)


enable_station.short_description = 'Включить станцию (если до этого выключали вручную)'


def activate_station(modeladmin, request, queryset):
    for parking_space in queryset:
        return HttpResponseRedirect(f"{settings.FRONTEND_BASE_URL}{settings.STATION_ACTIVATION}{parking_space.id}")


activate_station.short_description = 'Перейти на активацию станции'


class ParkingSpaceAdmin(admin.ModelAdmin):
    form = ParkingSpaceAdminForm
    inlines = [ParkingSpaceConnectorInline]
    list_display = (
        'uid',
        'name',
        'status',
        'mode',
        'current_a',
        'current_v',
        'total_kw',
        'is_occupied',
        'booking',
        'order',
        'is_manually_disabled',
    )
    list_filter = ['charge_type', 'status', 'mode']
    readonly_fields = [
        'status',
        'is_on',
        'booking',
        'order',
        'is_manually_disabled',
    ]
    actions = [disable_station, enable_station, activate_station]


admin.site.register(ParkingSpace, ParkingSpaceAdmin)


# ParkingSpaceStat
class ParkingSpaceStatAdminForm(forms.ModelForm):
    class Meta:
        model = ParkingSpaceStat
        fields = '__all__'


class ParkingSpaceStatAdmin(admin.ModelAdmin):
    form = ParkingSpaceStatAdminForm
    list_display = ('uuid', 'space', 'is_on', 'current_a', 'last_data_update')
    list_filter = ['status']
    readonly_fields = [
        'total_kw',
        'current_w',
        'current_v',
        'current_a',
        'created_at',
    ]


admin.site.register(ParkingSpaceStat, ParkingSpaceStatAdmin)


# Order
class OrderAdminForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'


class OrdersKwFilter(admin.SimpleListFilter):
    title = 'Заказы с кВт'
    parameter_name = 'total_kw'

    def lookups(self, request, model_admin):
        return [
            ('some', 'Тратили кВт'),
            ('zero', 'Не тратили кВт'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'some':
            return queryset.filter(_delta_kw__gt=0.01)
        if self.value() == 'zero':
            return queryset.filter(_delta_kw__lte=0.01)
        return None


class OrderAdmin(admin.ModelAdmin):
    form = OrderAdminForm
    list_filter = ['status', 'connector_type', 'created_at', OrdersKwFilter]
    search_fields = ['user__username']
    list_display = (
        'user',
        'space',
        'connector_type',
        'status',
        'cost_total',
        'created_at',
        'delta_kw',
        'duration',
    )
    readonly_fields = [
        'selected_camera',
        'space',
        'user',
        'start_payed',
        'start_kw',
        'cost_total',
        'connector_type',
        'payed_seconds',
        'payed_kw',
        'delta_kw',
        'duration',
        'created_at',
        'status',
    ]

    actions = [finish_order]
    ordering = ('-created_at',)


admin.site.register(Order, OrderAdmin)


# SmsSend
class SmsSendAdminForm(forms.ModelForm):
    class Meta:
        model = SmsSend
        fields = '__all__'


class SmsSendAdmin(admin.ModelAdmin):
    form = SmsSendAdminForm
    list_display = ('number', 'created')
    readonly_fields = ['created']
    search_fields = ['number']


admin.site.register(SmsSend, SmsSendAdmin)


# Camera
class CameraAdminForm(forms.ModelForm):
    class Meta:
        model = Camera
        fields = '__all__'


class CameraAdmin(admin.ModelAdmin):
    form = CameraAdminForm
    list_display = (
        'id',
        'img_preview',
        'ip',
        'name',
        'space',
        'last_image_update',
    )
    filter_list = ['space']
    search_fields = ['name']
    readonly_fields = ['image_iter', 'img_preview']


admin.site.register(Camera, CameraAdmin)


# Device
class DeviceAdminForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = '__all__'


class DeviceAdmin(admin.ModelAdmin):
    form = DeviceAdminForm
    list_display = ('name', 'key', 'space')
    readonly_fields = ['key']


admin.site.register(Device, DeviceAdmin)


def cancel_booking(modeladmin, request, queryset):
    for booking in queryset:
        user = booking.user
        booking.cancel()
        send_cancel_bookings(user)
        send_phone_auth_response(user, user)
    send_refills('all')


cancel_booking.short_description = 'Отменить бронирование'


class BookingAdminForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = '__all__'


class BookingAdmin(admin.ModelAdmin):
    form = BookingAdminForm
    search_fields = ['user__username']
    list_filter = ['operations__order__status', 'space']
    list_display = (
        'user',
        'status',
        'space',
        'connector',
        'created_at',
        'activated_at',
        'cancelled_at',
        'booked_until',
        'order',
        'actual_duration',
    )
    readonly_fields = (
        'user',
        'status',
        'connector',
        'space',
        'order',
    )
    actions = (cancel_booking,)
    ordering = ('-created_at',)


admin.site.register(Booking, BookingAdmin)


class ProviderAdminForm(forms.ModelForm):
    class Meta:
        model = Provider
        fields = '__all__'

    def __str__(self):
        return self.name


class ProviderAdmin(admin.ModelAdmin):
    form = ProviderAdminForm
    formfield_overrides = {
        JSONField: {'widget': JSONEditor},
    }
    search_fields = ['name']


admin.site.register(Provider, ProviderAdmin)


class ProviderParkingLotAdminForm(forms.ModelForm):
    class Meta:
        model = ProviderParkingLot
        fields = '__all__'

    def __str__(self):
        return self.name


class ProviderParkingLotAdmin(admin.ModelAdmin):
    form = ProviderParkingLotAdminForm
    filter_horizontal = ('providers',)


admin.site.register(ProviderParkingLot, ProviderParkingLotAdmin)
