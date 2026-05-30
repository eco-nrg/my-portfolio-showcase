import os
import time
from datetime import datetime, timezone

import requests
from py_scripts.config import get_settings
from py_scripts.custom_logger import logger
from kv.redis_kv import models

settings = get_settings()
url = settings.api_url + '/main/api/v1/space_force_stop'
sonic_car_distance = settings.sonic_car_distance
sonic_range_lower_threshold = sonic_car_distance
current_amper_upper_threshold = 1
session_duration_seconds_lower_threshold = 5 * 60


def send_force_stop_session():
    # TODO: replace with settings.api_token 
    # once we migrated to new device auth flow
    token_key = os.environ['TOKEN_KEY']
    try:
        logger.info('Send force session stop')
        req = requests.post(
            url,
            headers={'Authorization': 'Bearer ' + token_key},
            timeout=30,
        )
        req.raise_for_status()
    except Exception:
        logger.exception('Failed to send session_stop')


def get_now():
    return datetime.now(tz=timezone.utc)


last_time_not_ready = get_now()


def update():
    global last_time_not_ready
    session_is_in_progress = models.get_prop_value('METER__HAS_POWER', '0')
    if session_is_in_progress == '0':
        return

    now = get_now()
    sonic_range_avg = float(models.get_prop_value('DISTANCE__AVG', '0') or 0)
    current_amper = float(models.get_prop_value('METER__AM_VALUE', '0') or 0)
    session_started_time = datetime.fromisoformat(
        models.get_prop_value('ORDER_START_TIME', '1970-01-01') or '1970-01-01',
    )
    session_duration = (now - session_started_time).total_seconds()

    # Проверяем условия на вызов автофиниша
    should_autofinish = (
        sonic_range_avg > sonic_range_lower_threshold and
        current_amper < current_amper_upper_threshold and
        session_duration > session_duration_seconds_lower_threshold
    )
    logger.info(
        'update range=%d threshold=%.2f amper=%.2f duration=%d should=%s should_duration=%d',
        int(sonic_range_avg),
        sonic_range_lower_threshold,
        current_amper,
        int(session_duration),
        should_autofinish,
        int((get_now() - last_time_not_ready).total_seconds()),
    )

    # Если условие не выполнено, сохраняем текущий момент времени в переменную
    if not should_autofinish:
        last_time_not_ready = get_now()
        return

    # Если условие выполнено на протяжении 5ти минут,
    # то отправляем на сервер запрос о необходимости
    # принудительно завершить зарядку
    ready_duration_seconds = (
        get_now() - last_time_not_ready
    ).total_seconds()
    if ready_duration_seconds > 5 * 60:
        send_force_stop_session()


def main():
    logger.info('autofinish loop started')
    while True:
        update()
        time.sleep(5)


if __name__ == '__main__':
    main()
