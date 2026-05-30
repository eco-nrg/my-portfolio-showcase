import json
from http import HTTPStatus
from urllib.parse import quote

import requests
import structlog
from django.conf import settings

from main.models import SmsSend

MAX_SMS_LEN = 360
TRANSPORT = settings.SMS_TRANSPORT

logger = structlog.get_logger(__name__)


def send_sms(msg: str, to: str) -> SmsSend:
    if TRANSPORT == 'real':
        service_response = _send_sms_real(msg, to)
    else:
        service_response = _send_sms_stub(msg, to)

    return SmsSend.objects.create(
        number=to,
        text=msg,
        JSON_result=service_response,
    )


def _send_sms_stub(msg: str, to: str) -> str:
    logger.info('sms_stub', to=to, msg=msg)
    fake_resp = {
        'status': 'TEST',
        'status_code': 100,
        'sms': {
            to: {
                'status': 'OK',
                'status_code': 100,
                'sms_id': 'TEST_SMS_ID',
                'cost': '0.00',
                'sms': 1,
            },
        },
        'balance': 0,
    }
    return json.dumps(fake_resp)


def _send_sms_real(msg: str, to: str) -> str:
    url = 'http://sms.ru/sms/send?api_id={0}&to={1}&text={2}&json=1'
    try:
        text = msg[:MAX_SMS_LEN]
        txt = quote(text.encode('utf8'), ':/')
        req = requests.get(
            url.format(settings.SMS_API_KEY, to, txt),
            timeout=settings.REQUESTS_TIMEOUT,
        )
        if req.status_code == HTTPStatus.OK:
            res = req.json()
        else:
            res = {
                'status': 'FAIL',
                'cause': f'api respond with {req.status_code}',
            }
    except Exception as err:
        logger.exception('send_sms_failed')
        res = {'status': 'FAIL', 'cause': str(err)}
        # pass this exception

    logger.info('sms_api_response', data=res)

    try:
        service_response = json.dumps(res)
    except Exception:
        logger.exception('save_sms_json_failed')
        service_response = '{"cause": "Failed to parse json"}'

    return service_response
