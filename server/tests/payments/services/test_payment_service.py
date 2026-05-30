import pytest
import responses
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone

from payments.schemas import PaymentLinkType
from payments.services.models.exceptions import PaymentError
from payments.models import Payment, PaymentStatus, PaymentProcessingStatus, PaymentApiLog, PaymentApiLogType, \
    PaymentApiLogStatus
from payments.services.payments_service import create_payment_link

__base_url = settings.ALFA_BASE_URL
__minimum_payment = settings.MINIMUM_PAYMENT
__maximym_payment = settings.MAXIMUM_PAYMENT
__register_order_url = f'{__base_url}{settings.ALFA_REGISTER_PAYMENT}'
__get_sbp_link_url = f'{__base_url}{settings.ALFA_GET_SBP_LINK}'


@pytest.fixture()
def user():
    u = User.objects.create(username='79999999999')
    u.set_password('1234')
    u.save()
    u.profile.code = '1234'
    u.profile.last_code_sent = timezone.now()
    u.profile.first_name = 'first_name'
    u.profile.middle_name = 'middle_name'
    u.profile.car_manufacturer = 'Tesla'
    u.profile.car_model = 'Model X'
    u.profile.car_number = 'A777AA'
    u.profile.car_year = 2025
    u.profile.battery_power = 100
    u.profile.fast_type = 'CHADEMO'
    u.profile.slow_type = 'TESLA_US'
    u.profile.save()
    return u


@responses.activate
@pytest.mark.django_db(transaction=True)
def test_create_payment_link_success_with_card(
    user: User,
):
    amount = 100
    responses.add(
        responses.POST,
        url=__register_order_url,
        json={
            'formUrl': 'test_url',
            'orderId': 'test_id',
            'errorCode': '0'
        },
        status=200,
    )

    result = create_payment_link(user, amount, PaymentLinkType.card)

    assert result == 'test_url'

    payment_count = Payment.objects.count()
    assert payment_count == 1

    payment: Payment = Payment.objects.first()
    assert payment.status == PaymentStatus.PENDING
    assert payment.processing_status == PaymentProcessingStatus.PENDING_WEBHOOK
    assert payment.pay_amount == amount

    api_calls_count = PaymentApiLog.objects.filter(
        type=PaymentApiLogType.API_CALL,
    ).count()
    assert api_calls_count == 1

    api_log: PaymentApiLog = PaymentApiLog.objects.first()
    assert api_log.payment == payment
    assert api_log.type == PaymentApiLogType.API_CALL
    assert api_log.status == PaymentApiLogStatus.SUCCESS


@responses.activate
@pytest.mark.django_db(transaction=True)
def test_create_payment_link_success_with_sbp(
    user: User,
):
    amount = 100
    responses.add(
        responses.POST,
        url=__register_order_url,
        json={
            'formUrl': 'test_url',
            'orderId': 'test_id',
            'errorCode': '0'
        },
        status=200,
    )
    responses.add(
        responses.POST,
        url=__get_sbp_link_url,
        json={
            'payload': 'test_sbp_url',
        },
        status=200,
    )

    result = create_payment_link(user, amount, PaymentLinkType.sbp)

    assert result == 'test_sbp_url'

    payment_count = Payment.objects.count()
    assert payment_count == 1

    payment: Payment = Payment.objects.first()
    assert payment.status == PaymentStatus.PENDING
    assert payment.processing_status == PaymentProcessingStatus.PENDING_WEBHOOK
    assert payment.pay_amount == amount

    api_calls_count = PaymentApiLog.objects.filter(
        type=PaymentApiLogType.API_CALL,
        payment=payment,
        status=PaymentApiLogStatus.SUCCESS,
    ).count()
    assert api_calls_count == 2


@responses.activate
@pytest.mark.django_db(transaction=True)
def test_create_payment_link_request_exception(
    user: User,
):
    amount = 100
    exception = Exception('test exception')
    responses.add(
        responses.POST,
        url=__register_order_url,
        body=exception,
    )

    with pytest.raises(PaymentError) as payment_error:
        create_payment_link(user, amount, PaymentLinkType.card)

    assert (
        payment_error.value.msg == 'Не удалось подключиться к платежному серверу'
    )

    payment_count = Payment.objects.count()
    assert payment_count == 1

    payment: Payment = Payment.objects.first()
    assert payment.status == PaymentStatus.PENDING
    assert payment.processing_status == PaymentProcessingStatus.FAILED_LINK
    assert payment.pay_amount == amount

    api_calls_count = PaymentApiLog.objects.filter(
        type=PaymentApiLogType.API_CALL,
    ).count()
    assert api_calls_count == 1

    api_log: PaymentApiLog = PaymentApiLog.objects.first()
    assert api_log.payment == payment
    assert api_log.type == PaymentApiLogType.API_CALL
    assert api_log.status == PaymentApiLogStatus.FAILED


@responses.activate
@pytest.mark.django_db(transaction=True)
def test_create_payment_link_parse_json_exception(
    user: User,
):
    amount = 100
    responses.add(
        responses.POST,
        url=__register_order_url,
        status=200,
    )

    with pytest.raises(PaymentError) as payment_error:
        create_payment_link(user, amount, PaymentLinkType.card)

    assert (
        payment_error.value.msg == 'Не удалось получить информацию о заказе с платежного сервера'
    )

    payment_count = Payment.objects.count()
    assert payment_count == 1

    payment: Payment = Payment.objects.first()
    assert payment.status == PaymentStatus.PENDING
    assert payment.processing_status == PaymentProcessingStatus.FAILED_LINK
    assert payment.pay_amount == amount

    api_calls_count = PaymentApiLog.objects.filter(
        type=PaymentApiLogType.API_CALL,
    ).count()
    assert api_calls_count == 1

    api_log: PaymentApiLog = PaymentApiLog.objects.first()
    assert api_log.payment == payment
    assert api_log.type == PaymentApiLogType.API_CALL
    assert api_log.status == PaymentApiLogStatus.FAILED


@responses.activate
@pytest.mark.django_db(transaction=True)
def test_create_payment_link_json_parse_exception(
    user: User,
):
    amount = 100
    responses.add(
        responses.POST,
        url=__register_order_url,
        json='qwerty',
        status=200,
    )

    with pytest.raises(PaymentError) as payment_error:
        create_payment_link(user, amount, PaymentLinkType.card)

    assert (
        payment_error.value.msg == 'Не удалось получить информацию о заказе с платежного сервера'
    )

    payment_count = Payment.objects.count()
    assert payment_count == 1

    payment: Payment = Payment.objects.first()
    assert payment.status == PaymentStatus.PENDING
    assert payment.processing_status == PaymentProcessingStatus.FAILED_LINK
    assert payment.pay_amount == amount

    api_calls_count = PaymentApiLog.objects.filter(
        type=PaymentApiLogType.API_CALL,
    ).count()
    assert api_calls_count == 1

    api_log: PaymentApiLog = PaymentApiLog.objects.first()
    assert api_log.payment == payment
    assert api_log.type == PaymentApiLogType.API_CALL
    assert api_log.status == PaymentApiLogStatus.FAILED


@responses.activate
@pytest.mark.django_db(transaction=True)
def test_create_payment_link_incorrect_response_exception(
    user: User,
):
    amount = 100
    responses.add(
        responses.POST,
        url=__register_order_url,
        json={
            'test': 'test',
        },
        status=200,
    )

    with pytest.raises(PaymentError) as payment_error:
        create_payment_link(user, amount, PaymentLinkType.card)

    assert (
        payment_error.value.msg == 'Неправильный формат ответа от платежного сервера'
    )

    payment_count = Payment.objects.count()
    assert payment_count == 1

    payment: Payment = Payment.objects.first()
    assert payment.status == PaymentStatus.PENDING
    assert payment.processing_status == PaymentProcessingStatus.FAILED_LINK
    assert payment.pay_amount == amount

    api_calls_count = PaymentApiLog.objects.filter(
        type=PaymentApiLogType.API_CALL,
    ).count()
    assert api_calls_count == 1

    api_log: PaymentApiLog = PaymentApiLog.objects.first()
    assert api_log.payment == payment
    assert api_log.type == PaymentApiLogType.API_CALL
    assert api_log.status == PaymentApiLogStatus.FAILED


@responses.activate
@pytest.mark.django_db(transaction=True)
def test_create_payment_link_failed_response(
    user: User,
):
    amount = 100
    responses.add(
        responses.POST,
        url=__register_order_url,
        json={
            'errorCode': '5',
            'errorMessage': 'Все плохо!'
        },
        status=200,
    )

    with pytest.raises(PaymentError) as payment_error:
        create_payment_link(user, amount, PaymentLinkType.card)

    assert (
        payment_error.value.msg == 'Не удалось получить информацию о заказе с платежного сервера'
    )

    payment_count = Payment.objects.count()
    assert payment_count == 1

    payment: Payment = Payment.objects.first()
    assert payment.status == PaymentStatus.PENDING
    assert payment.processing_status == PaymentProcessingStatus.FAILED_LINK
    assert payment.pay_amount == amount

    api_calls_count = PaymentApiLog.objects.filter(
        type=PaymentApiLogType.API_CALL,
    ).count()
    assert api_calls_count == 1

    api_log: PaymentApiLog = PaymentApiLog.objects.first()
    assert api_log.payment == payment
    assert api_log.type == PaymentApiLogType.API_CALL
    assert api_log.status == PaymentApiLogStatus.FAILED


@pytest.mark.django_db(transaction=True)
def test_create_payment_link_error_amount_is_less_than_minimum(
    user: User,
):
    amount = __minimum_payment - 0.01
    with pytest.raises(PaymentError) as payment_error:
        create_payment_link(user, amount, PaymentLinkType.card)

    assert (
        payment_error.value.msg == 'Сумма платежа меньше минимальной'
    )

    payment_count = Payment.objects.count()
    assert payment_count == 0

    api_calls_count = PaymentApiLog.objects.filter(
        type=PaymentApiLogType.API_CALL,
    ).count()
    assert api_calls_count == 0


@pytest.mark.django_db(transaction=True)
def test_create_payment_link_error_amount_is_greater_than_maximum(
    user: User,
):
    amount = __maximym_payment + 0.01
    with pytest.raises(PaymentError) as payment_error:
        create_payment_link(user, amount, PaymentLinkType.card)

    assert (
        payment_error.value.msg == 'Сумма платежа больше максимальной'
    )

    payment_count = Payment.objects.count()
    assert payment_count == 0

    api_calls_count = PaymentApiLog.objects.filter(
        type=PaymentApiLogType.API_CALL,
    ).count()
    assert api_calls_count == 0
