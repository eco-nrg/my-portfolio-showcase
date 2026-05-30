import logging
import os

import sentry_sdk
import structlog
from sentry_sdk.integrations.logging import LoggingIntegration
from structlog_sentry import SentryProcessor

SENTRY_ENV = os.environ.get('SENTRY_ENV', 'local')
LOG_LEVEL_NAME = os.environ.get('LOG_LEVEL', 'info').lower()

logger_level = logging.DEBUG if LOG_LEVEL_NAME == 'debug' else logging.INFO

shared_structlog_processors = [
    structlog.contextvars.merge_contextvars,
    structlog.processors.TimeStamper(fmt='iso'),
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.stdlib.PositionalArgumentsFormatter(),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.UnicodeDecoder(),
    SentryProcessor(
        tag_keys=["logger", "level"]
    ),
]

logging.basicConfig(level=logger_level)

structlog.configure(
    processors=shared_structlog_processors + [
        structlog.dev.ConsoleRenderer(colors=True),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.stdlib.get_logger()

if os.environ.get('SENTRY_DSN', '') != '':
    sentry_sdk.init(
        dsn=os.environ['SENTRY_DSN'],
        environment=os.environ.get('SENTRY_ENV', 'local'),
        integrations=[
            # Не отправляем на sentry стандартные логи,
            # так как их отправляет сам structlog.SentryProcessor
            LoggingIntegration(event_level=None, level=None),
        ],

        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production,
        traces_sample_rate=0.25,
    )
