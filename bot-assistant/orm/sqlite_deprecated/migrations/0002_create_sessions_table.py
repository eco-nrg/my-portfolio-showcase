from peewee import SqliteDatabase
from orm.sqlite_deprecated.models.session_mapping import Session
from config import Config


_config = Config()

database = SqliteDatabase(_config.SQLITE_PATH_TO_DB)
database.create_tables([Session])
