from peewee import CharField

from config import Config
from orm.sqlite_deprecated.models.database_mapping import BaseModel

_config = Config()


class User(BaseModel):
    user_telegram_id = CharField(primary_key=True, column_name='UserTelegramID')
    full_name = CharField(column_name='FullName')

    def __str__(self):
        return f'User data:\nTelegram ID: {self.user_telegram_id}\nFull name: {self.full_name}'

    class Meta:
        table_name = _config.SQLITE_USERS_TABLE
