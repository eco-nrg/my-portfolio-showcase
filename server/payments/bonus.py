from types import MappingProxyType

from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from ninja import Schema
from pydantic import PositiveFloat

from payments.models import (
    BonusOperation,
    BonusOperationType,
    BonusSource,
    Operation,
    OperationAction,
    OperationType,
)


class BonusError(Exception):
    def __init__(self, msg) -> None:
        super().__init__()
        self.msg = msg


class ConvertBonusesRequest(Schema):
    amount: PositiveFloat


class ConvertBonusesResponse(Schema):
    msg: str
    balance: float
    bonus_balance: float


BONUS_DATA = MappingProxyType(
    {
        BonusSource.SIGN_UP: {
            'description': 'Бонус за регистрацию',
            'amount': 100,
        },
        BonusSource.FILL_PROFILE: {
            'description': 'Бонус за заполнение профиля',
            'amount': 100,
        },
    },
)


def add_bonuses_manually(user: User, amount: float):
    """Админский метод для добавления бонусов."""
    if amount <= 0:
        raise BonusError('Выбрано неверное количество бонусов для добавления')
    now = timezone.now()
    BonusOperation.objects.create(
        kind=BonusOperationType.DEBIT,
        source=BonusSource.MANUAL,
        user=user,
        description='Начисление бонусов',
        amount=amount,
        created_at=now,
    )
    return 'Ok'


def convert_bonuses(
    user: User,
    request: ConvertBonusesRequest,
):
    """Конвертация бонусов в деньги."""
    if user.profile.bonus_balance < request.amount:
        raise BonusError('Недостаточно бонусов на счету')
    now = timezone.now()

    # TODO Написать тест на атомарность операции
    with transaction.atomic():
        BonusOperation.objects.create(
            kind=BonusOperationType.CREDIT,
            user=user,
            description='Обмен бонусов на рубли',
            amount=request.amount,
            created_at=now,
        )
        Operation.objects.create(
            kind=OperationType.DEBIT,
            user=user,
            action=OperationAction.BONUS,
            amount=request.amount,
            created_at=now,
        )

    user.profile.refresh_from_db()
    return ConvertBonusesResponse(
        msg='Бонусы успешно конвертированы в рубли',
        balance=float(user.profile.balance),
        bonus_balance=float(user.profile.bonus_balance),
    )


@transaction.atomic
def add_fixed_bonus_singleton(source: BonusSource, user: User):
    bonus_not_received = BonusOperation.objects.filter(
        user=user,
        source=source,
    ).count()
    if bonus_not_received == 0:
        add_fixed_bonus_repeatable(source, user)


def add_fixed_bonus_repeatable(source: BonusSource, user: User):
    description = BONUS_DATA.get(source, {}).get('description')
    amount = BONUS_DATA.get(source, {}).get('amount')
    return BonusOperation.objects.create(
        kind=BonusOperationType.DEBIT,
        user=user,
        source=source,
        description=description,
        amount=amount,
        created_at=timezone.now(),
    )
