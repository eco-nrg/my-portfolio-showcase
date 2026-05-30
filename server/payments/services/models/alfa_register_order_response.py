from typing import Optional

from pydantic import BaseModel


class AlfaRegisterOrderResponse(BaseModel):
    """
    Модель которая представляет ответ от Альфы на регистрацию заказа

    https://alfa.rbsuat.com/payment/swagger/swagger.html#/register/registerOrder
    """

    """URL на форму оплаты"""
    formUrl: Optional[str] = None

    """id заказа в системе Альфы"""
    orderId: Optional[str] = None

    """Код ошибки, 0 или ничего - все ок. иначе плохо"""
    errorCode: Optional[str] = None

    """Сообщние об ошибки, если оно есть"""
    errorMessage: Optional[str] = None
