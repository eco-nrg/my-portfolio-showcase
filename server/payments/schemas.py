from enum import Enum

from ninja import Schema
from pydantic import PositiveFloat


# TODO: надо сделать слой общих моделей для WS и REST.
# Но так, чтобы WS не зависел от каких-то бибилиотек для REST
# В данном случае получается так, что Schema - это на самом деле Pydantic,
# но с обертками для REST. Теоретически это не нужно для WS
# Может получится в ninja использовать чистые Pydantic?

class PaymentLinkType(Enum):
    sbp = 'sbp'
    card = 'card'


class PaymentLinkRequest(Schema):
    amount: PositiveFloat
    type: PaymentLinkType


class PaymentLinkResponse(Schema):
    url: str
