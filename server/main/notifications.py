from decimal import Decimal

import structlog
from django.conf import settings

from main.order_snapshot import OrderSnapshot
from main.config.redis_provider import RedisProvider
from main.models.order import Order
from main.sms import send_sms

_logger = structlog.get_logger(__name__)


def once_key(name: str, order: Order):
    return f"{name}-{str(order.uuid)}"


def once(key: str, ttl: int = 86400):
    """
        Оператор идемпотентности
        key: ключ по которому ищут повторы
        ttl: секунд. время жизни блокировки повторного вызова.
        Хранилище должно удалять само вставленные объекты по проществии времени
    """
    redis = RedisProvider.get_connection()

    if redis.get(name=key) is None:
        redis.set(name=key, value="once", ex=ttl)
        return True
    return False


def remove_once(key: str) -> None:
    redis = RedisProvider.get_connection()

    if redis.get(name=key):
        redis.delete(key)


def once_notify_reed_not_installed(order: Order, penalty_cost: Decimal):
    key = once_key("notify_reed_not_installed", order)
    if once(key):
        notify_reed_not_installed(order, penalty_cost)


def once_notify_less_balance(order: Order, has_deposited: bool = False):
    _logger.info(
        'into once_notify_less_balance',
    )

    key = once_key("notify_less_balance", order)
    if once(key) and not has_deposited:
        notify_less_balance(order)

        _logger.info(
            'complete notify less balance',
        )
    elif not once(key) and has_deposited:
        remove_once(key)

        _logger.info(
            'complete removing key',
        )


def once_notify_no_money(order: Order):
    key = once_key("notify_no_money", order)
    if once(key):
        notify_no_money(order)


def once_notify_penalty_time(order: Order):
    key = once_key("notify_penalty_time", order)
    if once(key):
        notify_penalty_time(order)


def once_notify_no_night_charge(order: Order):
    key = once_key("notify_no_night_charge", order)
    if once(key):
        notify_no_night_charge(order)


def once_notify_end_session(order: Order):
    key = once_key("notify_end_session", order)
    if once(key):
        notify_end_session(order)


def notify_reed_not_installed(order: Order, penalty_cost: Decimal):
    user = order.user
    msg = (
        ''' 
        Внимание! По данным телеметрии, Вы завершили процесс зарядки. Однако, не вернули пистолет в держатель. 
        Сессия будет оставаться активной, пока Вы не приведёте оборудование в исходное состояние. Во избежание 
        начисления двойного простоя вернитесь и вставьте пистолет в держатель. После этого Вы сможете завершить 
        процесс зарядки. Спасибо. 
        '''
    )
    send_sms(msg, user.username)


def notify_less_balance(order: Order):
    user = order.user
    msg = (
        f'''
        Баланс Вашего Лицевого счёта менее {settings.LESS_BALANCE} рублей. Во избежание принудительного завершения 
        зарядки пополните баланс в web-приложении ({settings.FRONTEND_BASE_URL}{settings.PAYMENT_PAGE}) одним из 
        доступных способов. Рекомендуемый остаток лицевого счёта перед началом зарядки – {settings.RECOMMENDED_BALANCE} 
        рублей.
        '''
    )
    send_sms(msg, user.username)


def notify_no_money(order: Order):
    user = order.user
    msg = (
        f'''
        Недостаточно средств для продолжения зарядки, зарядка автомобиля прекращена, но простой продолжает 
        начисляться во избежание глубоко минуса завершите сессию и уберите автомобиль с парковки. Для продолжения 
        зарядки пополните баланс в web-приложении ({settings.FRONTEND_BASE_URL}{settings.PAYMENT_PAGE}) 
        одним из доступных способов и начните новую сессию.
        '''
    )
    send_sms(msg, user.username)


def notify_penalty_time(order: Order):
    user = order.user
    msg = (
        'Внимание! Вы завершили зарядную сессию. Однако, по данным телеметрии, Ваш электромобиль по-прежнему занимает '
        'парковку зарядного терминала. Во избежание начисления простоя в двойном размере УБЕРИТЕ ВАШЕ ТРАНСПОРТНОЕ '
        'СРЕДСТВО в течение 10 минут. Спасибо.'
    )
    send_sms(msg, user.username)


def notify_no_night_charge(order: Order):
    user = order.user
    msg = (
        'Внимание! Ток зарядки существенно снизился. Вероятно, зарядка подходит к концу. С 9:00, кроме стоимости '
        'зарядки, начнётся начисление оплаты за стоянку согласно тарифу для данной станции.'
    )
    send_sms(msg, user.username)


def notify_end_session(order: Order):
    user = order.user
    msg = (
        'Внимание! Ток заряда существенно снизился. Вероятно, зарядка подходит к концу. Через 15 минут, '
        'кроме стоимости зарядки, начнётся начисление оплаты за стоянку согласно тарифу для данной станции.'
    )
    send_sms(msg, user.username)
