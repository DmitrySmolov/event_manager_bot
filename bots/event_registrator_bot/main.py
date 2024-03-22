import asyncio
import logging

from aiohttp import web
from aiogram import Bot, Dispatcher

from config import BotCommands, config
from handlers import router

WEBHOOK_HOST = 'localhost'
WEBHOOK_PORT = 8080
WEBHOOK_ENDPOINT = '/db_status/'

EVENT_CONFIRMED_TXT = (
    'Поздравляем!\n\n'
    'Ваше мероприятие "{event_name}" подтверждено.'
)
EVENT_REJECTED_TXT = (
    'К сожалению, ваше мероприятие "{event_name}" отклонено.'
)

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.event_registrator_bot_token.get_secret_value())

dp = Dispatcher()
dp.include_router(router)


async def handle_db_status(request: web.Request):
    data = await request.json()
    logging.info(data)
    event_name = data.get('event_name')
    status = data.get('status')
    created_by_tg_id = data.get('created_by_tg_id')
    if status == 'CONFIRMED':
        await bot.send_message(
            chat_id=created_by_tg_id,
            text=EVENT_CONFIRMED_TXT.format(event_name=event_name)
        )
    elif status == 'REJECTED':
        await bot.send_message(
            chat_id=created_by_tg_id,
            text=EVENT_REJECTED_TXT.format(event_name=event_name)
        )
    return web.Response(status=200)


async def start_webhook_dispatcher():
    app = web.Application()
    app.add_routes([
        web.post(
            path=WEBHOOK_ENDPOINT,
            handler=handle_db_status,
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
