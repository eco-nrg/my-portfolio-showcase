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
table_name = _config.SQLITE_USERS_TABLE

migrate(
    migrator.drop_not_null(table_name, 'FirstName'),
    migrator.drop_not_null(table_name, 'SecondName'),
    migrator.drop_not_null(table_name, 'UserName'),
)
