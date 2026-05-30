from typing import Optional

from pydantic import BaseModel


class AlfaGetSbpLinkResponse(BaseModel):
    """
        Модель которую предоставляет Альфа банк в ответ на получение зарегестрированного в системе СБП QR-кода

        https://alfa.rbsuat.com/payment/swagger/swagger.html#/sbp_c2b/getDynamicQrUsingPOST
    """

    """Ссылка на QR-код"""
    payload: Optional[str] = None

    """Код ошибки, 0 или ничего - все ок. иначе плохо"""
    errorCode: Optional[str] = None

    """Сообщние об ошибки, если оно есть"""
    errorMessage: Optional[str] = None
