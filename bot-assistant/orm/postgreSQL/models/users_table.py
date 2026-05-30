from peewee import CharField

from orm.postgreSQL.models.base import BaseModel
from config import Config

_config = Config()


class User(BaseModel):
    user_telegram_id = CharField(primary_key=True, column_name='UserTelegramID')
    first_name = CharField(column_name='FirstName', null=True)
    second_name = CharField(column_name='SecondName', null=True)
    user_name = CharField(column_name='UserName', null=True)

    def __str__(self):
        return (
            'User data:\n'
            f'Telegram ID: {self.user_telegram_id}\n'
            f'Full name: {self.first_name} {self.second_name}\n'
            f'User name: {self.user_name}\n'
        )

    class Meta:
        table_name = _config.SQLITE_USERS_TABLE
        schema = 'public'
