from peewee import UUIDField, ForeignKeyField, CharField, TimestampField, BooleanField
from assistant_bot.bot_choices import DetailedQuestions
from orm.sqlite_deprecated.models.database_mapping import BaseModel
from orm.sqlite_deprecated.models.users_mapping import User
from config import Config
import uuid

_config = Config()


class Session(BaseModel):
    QUESTION_CHOICES = (
        (DetailedQuestions.FILL_PROFILE, ),
        # (DetailedQuestions.REPLENISH_BALANCE, DetailedQuestions.REPLENISH_BALANCE),
        # (DetailedQuestions.BONUS_SYSTEM, DetailedQuestions.BONUS_SYSTEM),
        (DetailedQuestions.CHARGING_NOT_STARTING, ),
        (DetailedQuestions.PARKLOCK_NOT_GO_DOWN, ),
        (DetailedQuestions.STATION_ACTIVE_NOT_CHARGING, ),
        (DetailedQuestions.CHARGING_SESSION_NOT_END, ),
        (DetailedQuestions.REQUIRES_GERKON_BUT_INSERTED, ),
        (DetailedQuestions.OTHER_QUESTION, ),
    )

    # TODO: replace uuid to a little bit shorter id key
    session_id = UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        column_name='SessionId'
    )
    user = ForeignKeyField(
        User,
        backref='sessions'
    )
    question = CharField(
        choices=QUESTION_CHOICES
    )
    place = CharField(
        column_name='Place'
    )
    connector = CharField(
        column_name='Connector'
    )
    asked_in = TimestampField(
        column_name='AskedIn'
    )
    is_solved = BooleanField(
        column_name='IsSolved',
        default=False,
        null=False,
    )
    solved_at = TimestampField(
        column_name='SolvedAt'
    )

    def __str__(self):
        return (
            'Session is:\n'
            f'session_id={self.session_id}\n'
            f'user={self.user}\n'
            f'question={self.question}\n'
        )

    class Meta:
        table_name = _config.SQLITE_SESSIONS_TABLE
