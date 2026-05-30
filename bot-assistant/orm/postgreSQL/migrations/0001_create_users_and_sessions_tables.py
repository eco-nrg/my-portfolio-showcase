from peewee import PostgresqlDatabase
import structlog

from config import Config
from orm.postgreSQL.models.sessions_table import Session
from orm.postgreSQL.models.users_table import User

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

database.connect()
database.create_tables([User, Session])

database.close()
