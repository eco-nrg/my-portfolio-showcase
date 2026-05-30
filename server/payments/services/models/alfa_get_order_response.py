from typing import Optional

from pydantic import BaseModel


class AlfaGetOrderResponse(BaseModel):
    """
        Модель которая представляет ответ от Альфы на получение заказа

        https://alfa.rbsuat.com/payment/swagger/swagger.html#/status/getOrderStatusExtended
        """

    """
    Состояние заказа в платёжной системе. Отсутствует, если заказ не был найден. Список возможных значений:
    0 - Заказ зарегистрирован, но не оплачен;
    1 - Предавторизованная сумма захолдирована (для двухстадийных платежей);
    2 - Проведена полная авторизация суммы заказа;
    3 - Авторизация отменена;
    4 - По транзакции была проведена операция возврата;
    5 - Инициирована авторизация через ACS банка-эмитента;
    6 - Авторизация отклонена.
    """
    orderStatus: Optional[int] = None

    """Код ошибки, 0 или ничего - все ок. иначе плохо"""
    errorCode: Optional[str] = None

    """Сообщние об ошибки, если оно есть"""
    errorMessage: Optional[str] = None
