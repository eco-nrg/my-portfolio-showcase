import structlog
from playhouse.migrate import *

from config import Config

_config = Config()
_logger = structlog.get_logger(__name__)

database_host = _config.POSTGRES_DB_HOST
database_name = _config.POSTGRES_DB_NAME
database_user = _config.POSTGRES_DB_USER
database_password = _config.POSTGRES_DB_PASSWORD

_logger.info(
    'init migration with data for database',
    url=_config.POSTGRES_DB_URL,
    user=database_user,
    host=database_host,
    name=database_name,
    password=database_password,
)

database = PostgresqlDatabase(
    database_name,
    user=database_user,
    password=database_password,
    host=database_host,
    port=5432,
)

_logger.info(
    'make connection tunnel to database',
    connection=database,
)

migrator = PostgresqlMigrator(database)
table = _config.SQLITE_USERS_TABLE
full_name = CharField(column_name='FullName')
first_name = CharField(column_name='FirstName', default='')
second_name = CharField(column_name='SecondName', default='')
user_name = CharField(column_name='UserName', default='')

migrate(
    migrator.drop_column(
        table,
        'FullName',
        full_name,
    ),
    migrator.add_column(
        table,
        'FirstName',
        first_name,
    ),
    migrator.add_column(
        table,
        'SecondName',
        second_name,
    ),
    migrator.add_column(
        table,
        'UserName',
        user_name,
    )
)
