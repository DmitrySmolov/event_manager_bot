import asyncio
from http import HTTPStatus
import logging

from aiohttp import web
from aiogram import Bot, Dispatcher

from config import BotCommands, config

WEBHOOK_HOST = 'localhost'
WEBHOOK_PORT = 8080
WEBHOOK_ENDPOINT = '/db_event/'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.event_status_updater_bot_token.get_secret_value())

dp = Dispatcher()


async def handle_db_event(request: web.Request):
    data = await request.json()
    logging.info(data)
    await bot.send_message(
        chat_id=config.admin_chat_id.get_secret_value(),
        text=f"New event: {data}"
    )
    return web.Response(status=HTTPStatus.OK)


async def start_webhook_dispatcher():
    app = web.Application()
    app.add_routes([
        web.post(
            path=WEBHOOK_ENDPOINT,
            handler=handle_db_event,
        )
    ])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(
        runner=runner,
        host=WEBHOOK_HOST,
        port=WEBHOOK_PORT
    )
    await site.start()


async def main():
    await bot.delete_my_commands()
    await bot.set_my_commands(
        commands=BotCommands.get_commands()
    )
    await start_webhook_dispatcher()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
