from enum import Enum
from typing import Optional

from ninja import Schema


class WebhookTypes(Enum):
    # операция удержани (холдирования) суммы
    approved = 'approved'
    # операция завершения
    deposited = 'deposited'
    # операция отмены
    reversed = 'reversed'
    # операция возврата
    refunded = 'refunded'
    # истекло время, отпущенное на оплату заказа
    declinedByTimeout = 'declinedByTimeout'


class WebhookParameters(Schema):
    # Номер заказа в системе альфа банка 6
    mdOrder: str = None
    # Номер заказа в нашей системе, его UUID 9
    orderNumber: str = None
    # Контрольная сумма для проверки 3, но не учитывается в строке
    checksum: str = None
    # Время создания данного callback'а 2
    callbackCreationDate: str = None
    # Тип операции 7
    operation: WebhookTypes = None
    # Статус операции. 0 - ошибка, 1 - все ок 10
    status: int
    # id связки 1
    bindingId: Optional[str] = None
    # id клиента 4
    clientId: Optional[str] = None
    # Активна ли связка 5
    enabled: Optional[bool] = None
    # Сумма частичного возврата в копейка(?) 8
    operationRefundedAmount: Optional[str] = None
    # Сумма частичного возврата в копейка и отформатированная 9
    operationRefundedAmountFormatted: Optional[str] = None

