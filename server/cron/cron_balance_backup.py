from typing import List, Tuple
import os

from account.models.profile import Profile

from django.db.models import QuerySet
from django.utils import timezone
from structlog import get_logger

PATH_TO_BACKUPS = "/code/backups/"
_logger = get_logger(__name__)

def create_balance_backup() -> None:
    profiles = get_all_profiles()
    profile_balances = []
    _logger.info('Start balance backup')
    try:
        for profile in profiles:
            balance = get_profile_balance(profile)
            profile_balances.append((profile.user.username, balance))
        write_to_file(profile_balances)
    except Exception as e:
        _logger.exception('Failed to create backup of balances', e=e)
    _logger.info('Finish balance backup')

def get_all_profiles() -> QuerySet:
    profile_list = Profile.objects.all()
    return profile_list

def get_profile_balance(profile: Profile) -> float:
    return profile.balance

def write_to_file(user_balances: List[Tuple]) -> None:
    current_time = timezone.now()
    os.makedirs(PATH_TO_BACKUPS, exist_ok=True)
    with open(f"{PATH_TO_BACKUPS}balance_backups_{current_time}.txt", "w+") as f:
        f.write("User, balance\n")
        for entry in user_balances:
            f.write(f"{entry[0]}, {entry[1]}\n")
