from datetime import datetime

from playhouse.migrate import SqliteMigrator, migrate, TimestampField, BooleanField
from peewee import SqliteDatabase
from config import Config


_config = Config()
database = SqliteDatabase(_config.SQLITE_PATH_TO_DB)
table = _config.SQLITE_SESSIONS_TABLE

migrator = SqliteMigrator(database)

with database.transaction():
    migrate(
        migrator.add_column(
            table,
            'asked_in',
            TimestampField(
                column_name='AskedIn',
                default=datetime.now(),
            )
        ),
        migrator.add_column(
            table,
            'is_solved',
            BooleanField(
                column_name='IsSolved',
                default=False,
                null=False,
            )
        ),
        migrator.add_column(
            table,
            'solved_at',
            TimestampField(
                column_name='SolvedAt',
                default=datetime.now(),
            )
        )
    )
