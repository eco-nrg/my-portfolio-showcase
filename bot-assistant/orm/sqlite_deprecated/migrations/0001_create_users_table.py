from peewee import SqliteDatabase
from orm.sqlite_deprecated.models.users_mapping import User
from config import Config


_config = Config()
db = SqliteDatabase(_config.SQLITE_PATH_TO_DB)

db.create_tables([User])
