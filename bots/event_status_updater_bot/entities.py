from pydantic import BaseModel


class PydanticEvent(BaseModel):
    """Модель события."""
    name: str | None = None
    location: str | None = None
    host: dict | None = None
    created_by: dict | None = None

    def to_user_friendly_str(self) -> str:
        h_username = self.host.get('username', 'не указан')
        h_telegram_id = self.host.get('telegram_id', 'не указан')
        cb_username = self.created_by.get('username', 'не указан')
        cb_telegram_id = self.created_by.get('telegram_id', 'не указан')
        return (
            f'Название : {self.name}\n'
            f'Локация: {self.location}\n'
            f'Ведущий: username {h_username}, telegram_id {h_telegram_id}\n'
            f'Создал: username: {cb_username}, telegram_id: {cb_telegram_id}'
        )
