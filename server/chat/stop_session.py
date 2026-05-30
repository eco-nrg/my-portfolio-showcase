from django.contrib.auth.models import User

from main.models import ORDER_STATUSES, Order


class StopSessionError(Exception):
    msg: str

    def __init__(self, msg: str = "Ошибка завершения зарядки") -> None:
        self.msg = msg


def stop_session(user: User):
    order = (
        Order.objects.filter(
            user=user,
            status=ORDER_STATUSES.ACTIVE,
        )
        .order_by("-created_at")
        .first()
    )

    if order is None:
        raise StopSessionError("Заказ уже завершен")

    if not order.space.is_reed_installed:
        raise StopSessionError("Пистолет не вставлен")

    order.finish(ORDER_STATUSES.FINISHED)
    return {"id": order.space.id}
