from playhouse.migrate import SqliteMigrator, migrate, CharField
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
            'place',
            CharField(column_name='Place', default='undefined'),
        ),
        migrator.add_column(
            table,
            'connector',
            CharField(column_name='Connector', default='undefined'),
        )
    )
