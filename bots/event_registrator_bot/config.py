from enum import Enum
import os
from pathlib import Path

from aiogram.types import BotCommand
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

BASE_DIR = Path(__file__).resolve().parent

ENV_FILE = os.path.join(BASE_DIR.parent.parent, '.env')

ENCODING = 'utf-8'

URL_PATTERN = (
    r'^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$'
)

API_URL_BASE = 'http://127.0.0.1:8000/api/'
EVENT_ENDPOINT = 'events/'


class Settings(BaseSettings):
    """
    Класс настроек приложения.
    """
    event_registrator_bot_token: SecretStr

    model_config = SettingsConfigDict(
        env_file=ENV_FILE, env_file_encoding=ENCODING, extra='ignore'
    )


class BotCommands(Enum):
    """
    Енум для хранения команд бота.
    """
    START = ('start', 'Начать заполнение формы регистрации мероприятия.')
    CANCEL = ('cancel', 'Отменить заполнение текущей формы.')

    @property
    def command(self) -> str:
        """Возвращает команду для бота."""
        return self.value[0]

    @property
    def description(self) -> str:
        """Возвращает описание команды."""
        return self.value[1]

    @classmethod
    def get_commands(cls) -> list[BotCommand]:
        """
        Возвращает список объектов BotCommand для метода бота
        `set_my_commands`.
        """
        return [
            BotCommand(
                command=cmd.command,
                description=cmd.description
            ) for cmd in cls
        ]


config = Settings()
