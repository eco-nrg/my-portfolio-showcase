from assistant_bot.assistant_bot import run_app
from orm.postgreSQL.models.base import BaseModel, connection
from config import Config
import structlog
import asyncio

_config = Config()
_logger = structlog.get_logger(__name__=__name__, __file__=__file__)


def bot_logger(function):
    def wrapper(*args, **kwargs):
        _logger.info('Start running assistant bot')
        _logger.info(
            'With connection',
            sqlite_database_url=_config.SQLITE_PATH_TO_DB,
            postgreSQL_database_url=_config.POSTGRES_DB_URL,
            database=BaseModel._meta.database,
            connection=connection,
        )
        try:
            return function(*args, **kwargs)
        except Exception as exc:
            _logger.error('Exception occurred', exc_info=exc)

    return wrapper


@bot_logger
def main():
    asyncio.run(run_app())


if __name__ == '__main__':
    main()
