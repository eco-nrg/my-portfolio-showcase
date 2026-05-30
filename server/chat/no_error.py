import structlog

logger = structlog.get_logger(__name__)


def no_error(func):
    def wrapper(self, *args, **kwargs):
        try:
            func(self, *args, **kwargs)
        except Exception:
            logger.exception('Failed inside no_error context')

    return wrapper
