from config import Config

from peewee import *
import structlog

_config = Config()
_logger = structlog.get_logger(__name__)

path_to_db = _config.SQLITE_PATH_TO_DB
_logger.info(
    f'path_to_db=${path_to_db}',
)

connection = SqliteDatabase(path_to_db)
_logger.info(
    f'connection=${connection}',
)


class BaseModel(Model):
    class Meta:
        database = connection


connection.close()
