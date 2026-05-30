import uuid
from datetime import timedelta

import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from payments.models import Payment, PaymentStatus, PaymentApiLog, PaymentApiLogType, PaymentApiLogStatus
from payments.models.webhook_parameters import WebhookParameters, WebhookTypes
from payments.services.models.exceptions import PaymentWebhookError
from payments.services.webhook_service import verify_event, __webhook_parameters_to_verify_string, __calculate_checksum


@pytest.fixture()
def user():
    code = '1234'
    user = User.objects.create(username='79999999999')
    user.set_password(code)
    user.save()
    user.profile.code = code
    user.profile.last_code_sent = timezone.now()
    user.profile.first_name = 'first_name'
    user.profile.middle_name = 'middle_name'
    user.profile.car_manufacturer = 'Tesla'
    user.profile.car_model = 'Model X'
    user.profile.car_number = 'A777AA'
    user.profile.car_year = 2025
    user.profile.battery_power = 100
    user.profile.fast_type = 'CHADEMO'
    user.profile.slow_type = 'TESLA_US'
    user.profile.save()
    return user


@pytest.fixture()
def payment(user: User):
    now = timezone.now()
    payment_expire_date = now + timedelta(days=2)
    return Payment.objects.create(
        user=user,
        pay_amount=100,
        created_at=now,
        expire_at=payment_expire_date,
        invoice_id='123456',
    )


@pytest.mark.django_db(transaction=True)
def test_verify_event_success_receive_one_deposited_event(
    payment: Payment,
):
    assert payment.status is PaymentStatus.PENDING
    req = WebhookParameters(
        mdOrder='1',
        orderNumber=str(payment.uuid),
        operation=WebhookTypes.deposited,
        status=1,
    )
    parameters_str = __webhook_parameters_to_verify_string(req)
    req.checksum = __calculate_checksum(parameters_str)
    verify_event(req)
    cnt = PaymentApiLog.objects.filter(
        type=PaymentApiLogType.WEBHOOK,
    ).count()
    assert cnt == 1
    payment.refresh_from_db()
    assert payment.status is PaymentStatus.PAID
    assert payment.user.profile.balance == payment.pay_amount


@pytest.mark.django_db(transaction=True)
def test_verify_event_success_receive_one_declined_by_timeout(
    payment: Payment,
):
    assert payment.status is PaymentStatus.PENDING
    req = WebhookParameters(
        mdOrder='1',
        orderNumber=str(payment.uuid),
        operation=WebhookTypes.declinedByTimeout,
        status=1,
    )
    parameters_str = __webhook_parameters_to_verify_string(req)
    req.checksum = __calculate_checksum(parameters_str)
    verify_event(req)
    cnt = PaymentApiLog.objects.filter(
        type=PaymentApiLogType.WEBHOOK,
    ).count()
    assert cnt == 1
    payment.refresh_from_db()
    assert payment.status is PaymentStatus.CANCELED
    assert payment.user.profile.balance == 0


@pytest.mark.django_db(transaction=True)
def test_verify_event_success_receive_one_deposited_but_failed_status(
    payment: Payment,
):
    assert payment.status is PaymentStatus.PENDING
    req = WebhookParameters(
        mdOrder='1',
        orderNumber=str(payment.uuid),
        operation=WebhookTypes.deposited,
        status=0,
    )
    parameters_str = __webhook_parameters_to_verify_string(req)
    req.checksum = __calculate_checksum(parameters_str)
    verify_event(req)
    cnt = PaymentApiLog.objects.filter(
        type=PaymentApiLogType.WEBHOOK,
    ).count()
    assert cnt == 1
    cnt = PaymentApiLog.objects.filter(
        status=PaymentApiLogStatus.SUCCESS,
    ).count()
    assert cnt == 1
    payment.refresh_from_db()
    assert payment.status is PaymentStatus.CANCELED
    assert payment.user.profile.balance == 0


@pytest.mark.django_db(transaction=True)
def test_verify_event_success_receive_one_declined_by_timeout_but_failed_status(
    payment: Payment,
):
    assert payment.status is PaymentStatus.PENDING
    req = WebhookParameters(
        mdOrder='1',
        orderNumber=str(payment.uuid),
        operation=WebhookTypes.declinedByTimeout,
        status=0,
    )
    parameters_str = __webhook_parameters_to_verify_string(req)
    req.checksum = __calculate_checksum(parameters_str)
    verify_event(req)
    cnt = PaymentApiLog.objects.filter(
        type=PaymentApiLogType.WEBHOOK,
    ).count()
    assert cnt == 1
    payment.refresh_from_db()
    assert payment.status is PaymentStatus.CANCELED
    assert payment.user.profile.balance == 0


@pytest.mark.django_db(transaction=True)
def test_verify_event_success_receive_several_deposited_events(
    payment: Payment,
):
    assert payment.status is PaymentStatus.PENDING
    req = WebhookParameters(
        mdOrder='1',
        orderNumber=str(payment.uuid),
        operation=WebhookTypes.deposited,
        status=1,
    )
    parameters_str = __webhook_parameters_to_verify_string(req)
    req.checksum = __calculate_checksum(parameters_str)
    verify_event(req)
    cnt = PaymentApiLog.objects.filter(
        type=PaymentApiLogType.WEBHOOK,
    ).count()
    assert cnt == 1
    log_status = PaymentApiLog.objects.filter(
        status=PaymentApiLogStatus.IGNORED,
    ).count()
    assert log_status == 0
    payment.refresh_from_db()
    assert payment.status is PaymentStatus.PAID
    assert payment.user.profile.balance == payment.pay_amount

    verify_event(req)
    cnt = PaymentApiLog.objects.filter(
        type=PaymentApiLogType.WEBHOOK,
    ).count()
    assert cnt == 2
    log_status = PaymentApiLog.objects.filter(
        status=PaymentApiLogStatus.IGNORED,
    ).count()
    assert log_status == 1
    payment.refresh_from_db()
    assert payment.status is PaymentStatus.PAID
    assert payment.user.profile.balance == payment.pay_amount

    verify_event(req)
    cnt = PaymentApiLog.objects.filter(
        type=PaymentApiLogType.WEBHOOK,
    ).count()
    assert cnt == 3
    log_status = PaymentApiLog.objects.filter(
        status=PaymentApiLogStatus.IGNORED,
    ).count()
    assert log_status == 2
    payment.refresh_from_db()
    assert payment.status is PaymentStatus.PAID
    assert payment.user.profile.balance == payment.pay_amount


@pytest.mark.django_db(transaction=True)
def test_verify_event_success_receive_several_canceled_by_timeout_events(
    payment: Payment,
):
    assert payment.status is PaymentStatus.PENDING
    req = WebhookParameters(
        mdOrder='1',
        orderNumber=str(payment.uuid),
        operation=WebhookTypes.declinedByTimeout,
        status=0,
    )
    parameters_str = __webhook_parameters_to_verify_string(req)
    req.checksum = __calculate_checksum(parameters_str)
    verify_event(req)
    cnt = PaymentApiLog.objects.filter(
        type=PaymentApiLogType.WEBHOOK,
    ).count()
    assert cnt == 1
    log_status = PaymentApiLog.objects.filter(
        status=PaymentApiLogStatus.IGNORED,
    ).count()
    assert log_status == 0
    payment.refresh_from_db()
    assert payment.status is PaymentStatus.CANCELED
    assert payment.user.profile.balance == 0

    verify_event(req)
    cnt = PaymentApiLog.objects.filter(
        type=PaymentApiLogType.WEBHOOK,
    ).count()
    assert cnt == 2
    log_status = PaymentApiLog.objects.filter(
        status=PaymentApiLogStatus.IGNORED,
    ).count()
    assert log_status == 1

    verify_event(req)
    cnt = PaymentApiLog.objects.filter(
        type=PaymentApiLogType.WEBHOOK,
    ).count()
    assert cnt == 3
    log_status = PaymentApiLog.objects.filter(
        status=PaymentApiLogStatus.IGNORED,
    ).count()
    assert log_status == 2


@pytest.mark.django_db(transaction=True)
def test_verify_event_success_receive_deposited_and_declined_by_timeout(
    payment: Payment,
):
    assert payment.status is PaymentStatus.PENDING
    deposited_req = WebhookParameters(
        mdOrder='1',
        orderNumber=str(payment.uuid),
        operation=WebhookTypes.deposited,
        status=1,
    )
    parameters_str = __webhook_parameters_to_verify_string(deposited_req)
    deposited_req.checksum = __calculate_checksum(parameters_str)
    verify_event(deposited_req)
    cnt = PaymentApiLog.objects.filter(
        type=PaymentApiLogType.WEBHOOK,
    ).count()
    assert cnt == 1
    log_status = PaymentApiLog.objects.filter(
        status=PaymentApiLogStatus.IGNORED,
    ).count()
    assert log_status == 0
    payment.refresh_from_db()
    assert payment.status is PaymentStatus.PAID
    assert payment.user.profile.balance == payment.pay_amount

    declined_by_timeout_req = WebhookParameters(
        mdOrder='1',
        orderNumber=str(payment.uuid),
        operation=WebhookTypes.declinedByTimeout,
        status=1,
    )
    parameters_str = __webhook_parameters_to_verify_string(declined_by_timeout_req)
    declined_by_timeout_req.checksum = __calculate_checksum(parameters_str)
    verify_event(declined_by_timeout_req)
    cnt = PaymentApiLog.objects.filter(
        type=PaymentApiLogType.WEBHOOK,
    ).count()
    assert cnt == 2
    log_status = PaymentApiLog.objects.filter(
        status=PaymentApiLogStatus.IGNORED,
    ).count()
    assert log_status == 1
    payment.refresh_from_db()
    assert payment.status is PaymentStatus.PAID
    assert payment.user.profile.balance == payment.pay_amount


@pytest.mark.django_db(transaction=True)
def test_verify_event_success_receive_declined_by_timeout_and_deposited(
    payment: Payment,
):
    assert payment.status is PaymentStatus.PENDING
    declined_by_timeout_req = WebhookParameters(
        mdOrder='1',
        orderNumber=str(payment.uuid),
        operation=WebhookTypes.declinedByTimeout,
        status=1,
    )
    parameters_str = __webhook_parameters_to_verify_string(declined_by_timeout_req)
    declined_by_timeout_req.checksum = __calculate_checksum(parameters_str)
    verify_event(declined_by_timeout_req)
    cnt = PaymentApiLog.objects.filter(
        type=PaymentApiLogType.WEBHOOK,
    ).count()
    assert cnt == 1
    log_status = PaymentApiLog.objects.filter(
        status=PaymentApiLogStatus.IGNORED,
    ).count()
    assert log_status == 0
    payment.refresh_from_db()
    assert payment.status is PaymentStatus.CANCELED
    assert payment.user.profile.balance == 0

    deposited_req = WebhookParameters(
        mdOrder='1',
        orderNumber=str(payment.uuid),
        operation=WebhookTypes.deposited,
        status=1,
    )
    parameters_str = __webhook_parameters_to_verify_string(deposited_req)
    deposited_req.checksum = __calculate_checksum(parameters_str)
    verify_event(deposited_req)
    cnt = PaymentApiLog.objects.filter(
        type=PaymentApiLogType.WEBHOOK,
    ).count()
    assert cnt == 2
    log_status = PaymentApiLog.objects.filter(
        status=PaymentApiLogStatus.IGNORED,
    ).count()
    assert log_status == 1
    payment.refresh_from_db()
    assert payment.status is PaymentStatus.CANCELED
    assert payment.user.profile.balance == 0


@pytest.mark.django_db(transaction=True)
def test_verify_event_ignore_refunded(
    payment: Payment,
):
    assert payment.status is PaymentStatus.PENDING
    req = WebhookParameters(
        mdOrder='1',
        orderNumber=str(payment.uuid),
        operation=WebhookTypes.refunded,
        status=1,
    )
    parameters_str = __webhook_parameters_to_verify_string(req)
    req.checksum = __calculate_checksum(parameters_str)
    verify_event(req)
    cnt = PaymentApiLog.objects.filter(
        type=PaymentApiLogType.WEBHOOK,
    ).count()
    assert cnt == 1
    log_status = PaymentApiLog.objects.filter(
        status=PaymentApiLogStatus.IGNORED,
    ).count()
    assert log_status == 1
    payment.refresh_from_db()
    assert payment.status is PaymentStatus.PENDING
    assert payment.user.profile.balance == 0


@pytest.mark.django_db(transaction=True)
def test_verify_event_ignore_reversed(
    payment: Payment,
):
    assert payment.status is PaymentStatus.PENDING
    req = WebhookParameters(
        mdOrder='1',
        orderNumber=str(payment.uuid),
        operation=WebhookTypes.reversed,
        status=1,
    )
    parameters_str = __webhook_parameters_to_verify_string(req)
    req.checksum = __calculate_checksum(parameters_str)
    verify_event(req)
    cnt = PaymentApiLog.objects.filter(
        type=PaymentApiLogType.WEBHOOK,
    ).count()
    assert cnt == 1
    log_status = PaymentApiLog.objects.filter(
        status=PaymentApiLogStatus.IGNORED,
    ).count()
    assert log_status == 1
    payment.refresh_from_db()
    assert payment.status is PaymentStatus.PENDING
    assert payment.user.profile.balance == 0


@pytest.mark.django_db(transaction=True)
def test_verify_event_ignore_approved(
    payment: Payment,
):
    assert payment.status is PaymentStatus.PENDING
    req = WebhookParameters(
        mdOrder='1',
        orderNumber=str(payment.uuid),
        operation=WebhookTypes.approved,
        status=1,
    )
    parameters_str = __webhook_parameters_to_verify_string(req)
    req.checksum = __calculate_checksum(parameters_str)
    verify_event(req)
    cnt = PaymentApiLog.objects.filter(
        type=PaymentApiLogType.WEBHOOK,
    ).count()
    assert cnt == 1
    log_status = PaymentApiLog.objects.filter(
        status=PaymentApiLogStatus.IGNORED,
    ).count()
    assert log_status == 1
    payment.refresh_from_db()
    assert payment.status is PaymentStatus.PENDING
    assert payment.user.profile.balance == 0


@pytest.mark.django_db(transaction=True)
def test_verify_event_invalid_checksum(
    payment: Payment,
):
    req = WebhookParameters(
        mdOrder='1',
        orderNumber=str(payment.uuid),
        operation=WebhookTypes.deposited,
        status=1,
        checksum='error',
    )
    with pytest.raises(PaymentWebhookError) as err:
        verify_event(req)
    assert err.value.msg == 'Check sum doesn\'t match'


@pytest.mark.django_db(transaction=True)
def test_verify_event_error_no_payment():
    req = WebhookParameters(
        mdOrder='1',
        orderNumber=str(uuid.uuid4()),
        operation=WebhookTypes.deposited,
        status=1,
    )
    parameters_str = __webhook_parameters_to_verify_string(req)
    req.checksum = __calculate_checksum(parameters_str)
    with pytest.raises(PaymentWebhookError) as err:
        verify_event(req)
    assert err.value.msg == 'Transaction not found'


def test_calculate_checksum_correct():
    req = WebhookParameters(
        mdOrder='039580ba-4cbc-7130-9b7f-052000bceae0',
        orderNumber='bb4cf500-ffc7-488d-9c2a-5a8469502782',
        operation=WebhookTypes.deposited,
        status=1,
        checksum='F15B870E35F4E628E192D7A9BC29EE2ED7B74B947613E12A6AA5D3B1EF583794'
    )
    parameters_str = __webhook_parameters_to_verify_string(req)
    checksum = __calculate_checksum(parameters_str)
    assert checksum == req.checksum
