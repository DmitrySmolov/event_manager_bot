from urllib.parse import urljoin

from aiohttp import ClientSession, ClientResponse

from config import config


async def udpate_event_status(
        event_id: int,
        status: str
) -> ClientResponse:
    """
    Обновляет статус мероприятия.
    """
    url_base = config.api_url_base.get_secret_value()
    endpoint = config.event_status_endpoint.get_secret_value().format(
        event_id=event_id
    )
    url = urljoin(url_base, endpoint)
    async with ClientSession() as session:
        response = await session.post(
            url=url,
            json={
                'status': status
            }
        )
        return response
