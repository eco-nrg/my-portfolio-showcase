import os

import structlog
from peewee_migrate import Router
from playhouse.postgres_ext import PostgresqlExtDatabase

from config import Config

_config = Config()
_logger = structlog.get_logger(__name__)

current_directory = os.path.dirname(os.path.abspath(__file__))
migrations_directory = os.path.join(current_directory, 'migrations')

_logger.info(
    'migration directory is %s',
    migrations_directory
)

database_name = _config.POSTGRES_DB_NAME
database_user = _config.POSTGRES_DB_USER
database_password = _config.POSTGRES_DB_PASSWORD
database_host = _config.POSTGRES_DB_HOST
database_port = 5432

db = PostgresqlExtDatabase(
    database_name,
    user=database_user,
    password=database_password,
    host=database_host,
    port=database_port,
)

router = Router(db, migrate_dir=migrations_directory)

router.run()

_logger.info('migration complete')
