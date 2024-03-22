import asyncio
from http import HTTPStatus
import logging

from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import CallbackQuery, Message

from api import udpate_event_status
from config import BotCommands, config
from entities import PydanticEvent
from keyboards import get_confirm_reject_keyboard
from utils import delete_inline_markup

WEBHOOK_HOST = 'localhost'
WEBHOOK_PORT = 8081
WEBHOOK_ENDPOINT = '/db_event/'
ADMIN_CHAT_ID = config.admin_chat_id.get_secret_value()

GREETINGS_TXT = (
    'Привет, {name}! Я буду присылать тебе оповещения о новых мероприятиях.'
)
NEW_EVENT_TXT = 'Зарегистрировано новое мероприятие:\n\n{event}'
UPDATE_STATUS_SUCCESS_TXT = (
    'Статус мероприятия успешно обновлен на "{status}"'
)
UPDATE_STATUS_FAIL_TXT = 'Не удалось обновить статус мероприятия'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.event_status_updater_bot_token.get_secret_value())

storage = MemoryStorage()

storage_key = StorageKey(
    bot_id=bot.id,
    chat_id=ADMIN_CHAT_ID,
    user_id=0,
)

dp = Dispatcher(storage=storage)


async def handle_db_event(request: web.Request):
    data = await request.json()
    logging.info(data)
    event_id = data.get('id')
    event = PydanticEvent()
    for field in event.model_fields:
        setattr(event, field, data.get(field, None))
    message = await bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=NEW_EVENT_TXT.format(event=event.to_user_friendly_str()),
        reply_markup=get_confirm_reject_keyboard().as_markup()
    )
    message_id = message.message_id

    await storage.set_data(
        key=storage_key,
        data={
            'event_id': event_id,
            'message_id': message_id
        }
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


@dp.message(CommandStart())
async def start(message: Message):
    """Запуск бота админом для возможности отправки ботом сообщений."""
    name = message.from_user.first_name
    await message.answer(
        text=GREETINGS_TXT.format(name=name)
    )


@dp.callback_query(F.data == 'confirm')
async def set_event_status_confirm(callback: CallbackQuery):
    """Подтверждение нового мероприятия."""
    data = await storage.get_data(key=storage_key)
    message_id = data['message_id']
    event_id = data['event_id']
    await delete_inline_markup(
        bot=bot,
        chat_id=ADMIN_CHAT_ID,
        message_id=message_id
    )
    try:
        response = await udpate_event_status(
            event_id=event_id,
            status='CONFIRMED'
        )
        if response.status == HTTPStatus.OK:
            await callback.answer(
                text=UPDATE_STATUS_SUCCESS_TXT.format(status='подтвержден'),
                show_alert=True
            )
        else:
            await callback.answer(
                text=UPDATE_STATUS_FAIL_TXT,
                show_alert=True
            )
    except Exception as e:
        logging.error(e)
        await callback.answer(
            text=UPDATE_STATUS_FAIL_TXT,
            show_alert=True
        )
    finally:
        await storage.set_data(key=storage_key, data={})


@dp.callback_query(F.data == 'reject')
async def set_event_status_reject(callback: CallbackQuery):
    """Отклонение нового мероприятия."""
    data = await storage.get_data(key=storage_key)
    message_id = data['message_id']
    event_id = data['event_id']
    await delete_inline_markup(
        bot=bot,
        chat_id=ADMIN_CHAT_ID,
        message_id=message_id
    )
    try:
        response = await udpate_event_status(
            event_id=event_id,
            status='REJECTED'
        )
        if response.status == HTTPStatus.OK:
            await callback.answer(
                text=UPDATE_STATUS_SUCCESS_TXT.format(status='отклонен'),
                show_alert=True
            )
        else:
            await callback.answer(
                text=UPDATE_STATUS_FAIL_TXT,
                show_alert=True
            )
    except Exception as e:
        logging.error(e)
        await callback.answer(
            text=UPDATE_STATUS_FAIL_TXT,
            show_alert=True
        )
    finally:
        await storage.set_data(key=storage_key, data={})


async def main():
    await bot.delete_my_commands()
    await bot.set_my_commands(
        commands=BotCommands.get_commands()
    )
    await start_webhook_dispatcher()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
