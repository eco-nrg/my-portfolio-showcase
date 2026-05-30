from playhouse.migrate import SqliteMigrator, migrate
from peewee import SqliteDatabase
from config import Config


_config = Config()
database = SqliteDatabase(_config.SQLITE_PATH_TO_DB)
table = _config.SQLITE_SESSIONS_TABLE

migrator = SqliteMigrator(database)

with database.transaction():
    migrate(
        migrator.rename_column(
            table,
            'place',
            'Place'
        ),
        migrator.rename_column(
            table,
            'connector',
            'Connector'
        ),
        migrator.rename_column(
            table,
            'asked_in',
            'AskedIn'
        ),
        migrator.rename_column(
            table,
            'is_solved',
            'IsSolved'
        ),
        migrator.rename_column(
            table,
            'solved_at',
            'SolvedAt'
        ),
    )
