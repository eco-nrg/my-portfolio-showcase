from django import forms
from django.contrib import admin, messages

from payments.services.models.exceptions import PaymentError
from payments.models import (
    BonusOperation,
    Operation,
    PaymentApiLog,
    Payment,
)
from payments.services.payments_service import full_refund_operation


class BonusOperationForm(forms.ModelForm):
    class Meta:
        model = BonusOperation
        fields = '__all__'


class BonusOperationAdmin(admin.ModelAdmin):
    form = BonusOperationForm
    list_display = ('user', 'kind', 'description', 'amount', 'created_at')
    list_filter = ['kind']
    search_fields = ['user__username']


admin.site.register(BonusOperation, BonusOperationAdmin)


class OperationForm(forms.ModelForm):
    class Meta:
        model = Operation
        fields = '__all__'


class OperationAdmin(admin.ModelAdmin):
    form = OperationForm
    list_display = ('user', 'kind', 'action', 'amount', 'created_at')
    list_filter = ['kind', 'action', 'created_at']
    search_fields = ['user__username']


admin.site.register(Operation, OperationAdmin)


def full_refund_money(modeladmin, request, queryset):
    try:
        for payment in queryset:
            full_refund_operation(payment)
    except PaymentError as e:
        messages.add_message(request, messages.WARNING, f'Ошибка: {str(e.msg)}')


full_refund_money.short_description = 'Выполнения полного возврата суммы'


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = (
            'processing_status',
            'expire_at',
            'paid_at',
            'canceled_at',
            'refunded_at',
        )


class PaymentAdmin(admin.ModelAdmin):
    form = PaymentForm
    readonly_fields = (
        'uuid',
        'user',
        'invoice_id',
        'invoice_url',
        'pay_amount',
        'created_at',
    )
    list_display = (
        'user',
        'invoice_id',
        'pay_amount',
        'processing_status',
        'created_at',
        'refunded_at',
        'display_status',
    )
    actions = [full_refund_money]
    list_filter = ['processing_status']
    search_fields = ['user__username']

    def display_status(self, payment: Payment):
        return payment.status

    display_status.short_description = 'Статус обработки'


admin.site.register(Payment, PaymentAdmin)


class PaymentApiLogForm(forms.ModelForm):
    class Meta:
        model = PaymentApiLog
        fields = '__all__'


class PaymentApiLogAdmin(admin.ModelAdmin):
    form = PaymentApiLogForm
    list_display = ('type', 'status', 'created_at', 'response_status')


admin.site.register(PaymentApiLog, PaymentApiLogAdmin)
