from enum import Enum
import os
from pathlib import Path

from aiogram.types import BotCommand
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

BASE_DIR = Path(__file__).resolve().parent

ENV_FILE = os.path.join(BASE_DIR.parent.parent, '.env')

ENCODING = 'utf-8'


class Settings(BaseSettings):
    """
    Класс настроек приложения.
    """
    event_status_updater_bot_token: SecretStr
    admin_chat_id: SecretStr
    api_url_base: SecretStr
    event_status_endpoint: SecretStr

    model_config = SettingsConfigDict(
        env_file=ENV_FILE, env_file_encoding=ENCODING, extra='ignore'
    )


class BotCommands(Enum):
    """
    Енум для хранения команд бота.
    """
    START = ('start', 'Начать работу.')

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
