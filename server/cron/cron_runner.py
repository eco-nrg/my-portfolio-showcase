import os
import sys
import time

import django
import schedule
import structlog

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'mywebsite.settings'

django.setup()

# Импорты СТРОГО после django.setup() так как используют ORM.
from cron.cron_booking import update_and_notify_booking_status  # noqa: E402
from cron.cron_charge_orders import charge_active_orders  # noqa: E402
from cron.cron_healthcheck_station import health_check_stations  # noqa: E402
from cron.cron_reset_free_minutes import reset_free_minutes  # noqa: E402
from cron.cron_check_payments import check_payments  # noqa: E402
from cron.cron_start_charging_parking import start_charging_parking  # noqa: E402
from cron.cron_charge_parking import charge_parking  # noqa: E402
from cron.cron_balance_backup import create_balance_backup

logger = structlog.get_logger('cron')


def main():
    logger.info('start cron_runner')
    schedule.every().day.at('00:01', 'Europe/Moscow').do(reset_free_minutes)
    schedule.every(1).seconds.do(charge_active_orders)
    schedule.every(1).seconds.do(start_charging_parking)
    schedule.every(1).seconds.do(charge_parking)
    schedule.every(1).seconds.do(health_check_stations)
    schedule.every(5).seconds.do(update_and_notify_booking_status)
    schedule.every(1).hours.do(check_payments)
    schedule.every(1).hours.do(create_balance_backup)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
