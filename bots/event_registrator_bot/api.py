from urllib.parse import urljoin

from aiohttp import ClientSession, ClientResponse

from config import config
from entities import PydanticEvent


async def create_new_event(
        event: PydanticEvent
) -> ClientResponse:
    """
    Создаёт новое мероприятие.
    """
    async with ClientSession() as session:
        response = await session.post(
            urljoin(
                config.api_url_base.get_secret_value(),
                config.event_endpoint.get_secret_value(),
            ),
            json=event.model_dump(),
        )
        return response
