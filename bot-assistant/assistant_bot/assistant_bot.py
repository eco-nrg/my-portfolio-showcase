import structlog
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from assistant_bot.handlers import questions
from config import Config
from orm.postgreSQL.models.sessions_table import Session

_config = Config()
_logger = structlog.get_logger(__name__)

bot_token = _config.TELEGRAM_BOT_TOKEN_KEY
bot_assistant = Bot(token=bot_token)
storage = MemoryStorage()
dispatcher = Dispatcher(storage=storage)


async def run_app():
    # TODO: IT IS MAIN TODO, in case when bot rebooting and any user keep talking to him all session's data cleans up

    dispatcher.include_routers(questions.router)

    await bot_assistant.delete_webhook(
        drop_pending_updates=True
    )

    await dispatcher.start_polling(
        bot_assistant,
        question_session=Session(),
        charging_space={},
    )

    _logger.info(
        'Bot successfully polling with data',
        routes=dispatcher.sub_routers,
        memory_storage=storage,
    )

