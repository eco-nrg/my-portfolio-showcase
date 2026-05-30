from decimal import Decimal


def clamp0Int(value: int) -> int:
    return value if value > 0 else 0


def clamp0Decimal(value: Decimal) -> Decimal:
    return value if value > 0 else Decimal(0)
