from playhouse.migrate import SqliteMigrator, migrate
from peewee import SqliteDatabase

from config import Config

_config = Config()
path_to_db = _config.SQLITE_PATH_TO_DB
table = _config.SQLITE_SESSIONS_TABLE
database = SqliteDatabase(path_to_db)

migrator = SqliteMigrator(database)

with database.transaction():
    migrate(
        migrator.drop_column(
            table,
            'asked_in',
        ),
        migrator.drop_column(
            table,
            'is_solved',
        ),
        migrator.drop_column(
            table,
            'solved_at',
        )
    )
