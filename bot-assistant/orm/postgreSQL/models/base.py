import structlog
from peewee import PostgresqlDatabase, Model

from config import Config

_config = Config()
_logger = structlog.get_logger(__name__)

database_host = _config.POSTGRES_DB_HOST
database_name = _config.POSTGRES_DB_NAME
database_user = _config.POSTGRES_DB_USER
database_password = _config.POSTGRES_DB_PASSWORD

_logger.info(
    'Database: ',
    url=_config.POSTGRES_DB_URL,
    host=database_host,
    user=database_user,
    password=database_password,
    database=database_name,
)

connection = PostgresqlDatabase(
    database_name,
    host=database_host,
    user=database_user,
    password=database_password,
    port=5432,
)


class BaseModel(Model):
    class Meta:
        database = connection


connection.close()
