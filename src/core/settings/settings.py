import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv


current_file_path = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
env_path = os.path.join(root_path, ".env")

load_dotenv(dotenv_path=env_path, override=True)


class Settings(BaseSettings):
    """Класс с настройками .env файла
    """
    DEBUG: bool
    RELOAD: bool
    VERSION: str
    DROP_TABLES: bool
    ECHO_SQL: bool
    
    NEED_STREAM_DATA: bool
    NEED_REQUEST_DATA: bool

    TITLE: str
    SUMMARY: str
    
    SERVER_IP: str
    SERVER_PORT: int

    DOCS_USERNAME: str
    DOCS_PASSWORD: str

    TG_LOG_TOKEN: str
    TG_LOG_CHANNEL: int
    
    DBASE_LOGIN: str
    DBASE_PASSWORD: str
    DBASE_IP: str
    DBASE_PORT: int
    DBASE_NAME: str

    DATABASE_APP_NAME: str
    DATABASE_URL: str
    REDIS_URL: str    
    
    model_config = SettingsConfigDict(env_file=env_path, env_file_encoding='utf-8')


settings = Settings()
