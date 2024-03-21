from pydantic import BaseModel


class PydanticEvent(BaseModel):
    """Модель события."""
    name: str
    location: str
    host: dict
    created_by: dict
