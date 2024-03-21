from urllib.parse import urljoin

from aiohttp import ClientSession, ClientResponse

from config import API_URL_BASE, EVENT_ENDPOINT
from entities import PydanticEvent


async def create_new_event(
        event: PydanticEvent
) -> ClientResponse:
    """
    Создаёт новое мероприятие.
    """
    async with ClientSession() as session:
        response = await session.post(
            urljoin(API_URL_BASE, EVENT_ENDPOINT),
            json=event.model_dump(),
        )
        return response
