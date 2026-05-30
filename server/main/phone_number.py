from typing import Optional

PHONE_LEN = 11
PHONE_COUNTRY_CODE = '7'


def check_number(phone: Optional[str]) -> Optional[str]:
    if not phone:
        return 'Номер не указан'

    if phone.startswith('+'):
        return 'Номер не должен начинаться со знака +'

    if len(phone) < PHONE_LEN:
        return 'Номер слишком короткий'

    if len(phone) > PHONE_LEN:
        return 'Номер слишком длинный'

    if phone[0] != PHONE_COUNTRY_CODE:
        return f'Отправка СМС только на номера с кодом +{PHONE_COUNTRY_CODE}'

    if not phone.isdigit():
        return 'После знака + номер должен содержать только цифры'

    return None
