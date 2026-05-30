import structlog

from account.models import Profile

logger = structlog.get_logger(__name__)


def reset_free_minutes():
    logger.info('reset_free_minutes')
    profiles = Profile.objects.all()

    for item in profiles:
        if item.can_charge_free:
            logger.info('reset_user', username=item.user.username)
            item.reset_limits()
