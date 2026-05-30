from peewee import UUIDField, ForeignKeyField, CharField, BooleanField, DateTimeField
from assistant_bot.bot_choices import DetailedQuestions
from orm.postgreSQL.models.base import BaseModel
from orm.postgreSQL.models.users_table import User

from config import Config

from uuid import uuid4

_config = Config()


class QuestionsAlias:
    FILL_PROFILE = 'FILL_PROFILE'
    CHARGING_NOT_STARTING = 'CHARGING_NOT_STARTING'
    PARKLOCK_NOT_GO_DOWN = 'PARKLOCK_NOT_GO_DOWN'
    STATION_ACTIVE_NOT_CHARGING = 'STATION_ACTIVE_NOT_CHARGING'
    CHARGING_SESSION_NOT_END = 'CHARGING_SESSION_NOT_END'
    REQUIRES_GERKON_BUT_INSERTED = 'REQUIRES_GERKON_BUT_INSERTED'
    OTHER_QUESTION = 'OTHER_QUESTION'

    ALIAS = {
        FILL_PROFILE: DetailedQuestions.FILL_PROFILE,
        CHARGING_NOT_STARTING: DetailedQuestions.CHARGING_NOT_STARTING,
        PARKLOCK_NOT_GO_DOWN: DetailedQuestions.PARKLOCK_NOT_GO_DOWN,
        STATION_ACTIVE_NOT_CHARGING: DetailedQuestions.STATION_ACTIVE_NOT_CHARGING,
        CHARGING_SESSION_NOT_END: DetailedQuestions.CHARGING_SESSION_NOT_END,
        REQUIRES_GERKON_BUT_INSERTED: DetailedQuestions.REQUIRES_GERKON_BUT_INSERTED,
        OTHER_QUESTION: DetailedQuestions.OTHER_QUESTION,
    }


class Session(BaseModel):
    QUESTION_CHOICES = (
        QuestionsAlias.FILL_PROFILE,
        QuestionsAlias.CHARGING_NOT_STARTING,
        QuestionsAlias.PARKLOCK_NOT_GO_DOWN,
        QuestionsAlias.STATION_ACTIVE_NOT_CHARGING,
        QuestionsAlias.CHARGING_SESSION_NOT_END,
        QuestionsAlias.REQUIRES_GERKON_BUT_INSERTED,
        QuestionsAlias.OTHER_QUESTION,
    )

    session_id = UUIDField(
        primary_key=True,
        default=uuid4(),
        column_name='SessionId'
    )
    user = ForeignKeyField(
        User,
        backref='sessions',
        column_name='UserTelegramID',
    )
    question = CharField(
        choices=QUESTION_CHOICES,
        column_name='Question',
    )
    place = CharField(
        column_name='Place'
    )
    connector = CharField(
        column_name='Connector'
    )
    asked_in = DateTimeField(
        column_name='AskedIn'
    )
    is_solved = BooleanField(
        column_name='IsSolved',
        default=False,
        null=False,
    )
    solved_at = DateTimeField(
        column_name='SolvedAt'
    )

    def __str__(self):
        return (
            'Session is:\n'
            f'session_id={self.session_id}\n'
            f'user={self.user}\n'
            f'question={self.question}\n'
            f'asked in={self.asked_in}\n'
        )

    class Meta:
        table_name = _config.SQLITE_SESSIONS_TABLE
        schema = 'public'
