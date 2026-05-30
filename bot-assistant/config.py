from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Optional
import structlog

_logger = structlog.get_logger(__name__)

env_file_locations = (
    str(Path(__file__).resolve().parent / '.env'),
)

_logger.info(
    'Check env`s file locations',
    env_file_locations=env_file_locations
)


class Config(BaseSettings):
    class Config:
        env_file = None
    # model_config = SettingsConfigDict(
    #     env_file=env_file_locations,
    #     env_file_encoding='utf-8',
    # )
    TELEGRAM_BOT_TOKEN_KEY: Optional[str]
    REPORT_PROBLEM_URL: Optional[str]
    API_TOKEN: Optional[str]
    API_SERVER_URL: Optional[str]
    API_BASE_PATH: Optional[str]
    API_VERSION: Optional[str]
    API_SPACES_PATH: Optional[str]
    API_ALL_SPACES_PATH: Optional[str]

    SQLITE_PATH_TO_DB: Optional[Path]
    SQLITE_USERS_TABLE: Optional[str]
    SQLITE_SESSIONS_TABLE: Optional[str]

    POSTGRES_DB_URL: Optional[str]
    POSTGRES_DB_HOST: Optional[str]
    POSTGRES_DB_NAME: Optional[str]
    POSTGRES_DB_USER: Optional[str]
    POSTGRES_DB_PASSWORD: Optional[str]

    BOT_TEXTS_START_MESSAGE: Optional[str]
    BOT_TEXTS_UNEXPECTED_ERROR: Optional[str]
    BOT_TEXTS_CHOOSE_CONNECTOR_MESSAGE: Optional[str]
    BOT_TEXTS_CHOOSE_QUESTION_MESSAGE: Optional[str]
