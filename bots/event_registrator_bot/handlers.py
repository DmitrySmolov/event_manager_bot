from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.types import (
    KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
)

from api import create_new_event
from config import BotCommands, URL_PATTERN
from entities import PydanticEvent

START_CONVERSATION_TXT = (
    'Добро пожаловать в бота регистрации мероприятий!\n\n'
    'Вы можете остановить регистрацию в любой момент, нажав на кнопку '
    '"/cancel" в меню.\n\n'
    'Для начала регистрации мероприятия введите его название.\n'
    '(не более 100 символов)'
)
INCORRECT_NAME_TXT = (
    'Название мероприятия не должно быть пустым или длиннее 100 символов.\n\n'
    'Попробуйте ещё раз.'
)
PROMPT_ENTER_LOCATION_TXT = (
    'Спасибо!\n\n'
    'Теперь введите ссылку на локацию мероприятия.\n'
    '(например, https://maps.app.goo.gl/tVJsR2zQX9gHNhMx8)'
)
INCORRECT_LOCATION_TXT = (
    'Ссылка на локацию должна быть валидной.\n\n'
    'Попробуйте ещё раз.'
)
PROMPT_ENTER_HOST_TXT = (
    'Спасибо!\n\n'
    'Теперь нам нужно узнать, кто будет ведущим мероприятия.\n'
    'Если им будете вы, то нажмите на кнопку "Отправить мой контакт".\n'
    'Либо прикрепите контакт другого пользователя Телеграм и отправьте '
    'сообщение.'
)
SEND_MY_CONTACT_KBOARD = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(
        text='Отправить мой контакт',
        request_contact=True
    )]],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder=(
        'Нажмите для отправки своего контакта либо закрепите контакт '
        'другого пользователя Телеграм в ответе.'
    )
)
INCORRECT_HOST_TXT = (
    'Для ведущего мероприятия необходимо указать контакт пользователя '
    'Телеграм.\n\n'
    'Попробуйте ещё раз.'
)
REGISTRATION_SUCCESS_TXT = (
    'Мероприятие успешно зарегистрировано!\n'
    'Ожидайте подтверждения администратора.\n'
    'Спасибо, что воспользовались нашим сервисом!'
)
REGISTRATION_FAILED_TXT = (
    'Что-то пошло не так. Попробуйте ещё раз позже.'
)
REGISTRATION_ABORTED_TXT = (
    'Регистрация мероприятия отменена.'
)
NOTHING_TO_CANCEL_TXT = (
    'Сейчас нет активных регистраций мероприятий.'
)

router = Router()


class EventRegistratorStates(StatesGroup):
    wait_for_name = State()
    wait_for_location = State()
    wait_for_host = State()


@router.message(default_state, CommandStart())
async def start_conversation(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text=START_CONVERSATION_TXT
    )
    await state.set_state(EventRegistratorStates.wait_for_name)


@router.message(Command(BotCommands.CANCEL.command))
async def cancel_registration(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state in [
        EventRegistratorStates.wait_for_name.state,
        EventRegistratorStates.wait_for_location.state,
        EventRegistratorStates.wait_for_host.state,
    ]:
        await state.clear()
        await message.answer(
            text=REGISTRATION_ABORTED_TXT,
            reply_markup=ReplyKeyboardRemove()
        )
        return
    await message.answer(
        text=NOTHING_TO_CANCEL_TXT,
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(
    EventRegistratorStates.wait_for_name,
    F.text & F.text.len().func(
        lambda length: length <= 100
    ) & ~F.text.startswith('/')
)
async def got_correct_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(
        text=PROMPT_ENTER_LOCATION_TXT
    )
    await state.set_state(EventRegistratorStates.wait_for_location)


@router.message(
    EventRegistratorStates.wait_for_name
)
async def got_incorrect_name(message: Message):
    await message.answer(INCORRECT_NAME_TXT)
    return


@router.message(
    EventRegistratorStates.wait_for_location,
    F.text & F.text.regexp(pattern=URL_PATTERN)
)
async def got_correct_location(message: Message, state: FSMContext):
    await state.update_data(location=message.text)
    await message.answer(
        text=PROMPT_ENTER_HOST_TXT,
        reply_markup=SEND_MY_CONTACT_KBOARD
    )
    await state.set_state(EventRegistratorStates.wait_for_host)


@router.message(
    EventRegistratorStates.wait_for_location
)
async def got_incorrect_location(message: Message):
    await message.answer(INCORRECT_LOCATION_TXT)
    return


@router.message(
    EventRegistratorStates.wait_for_host,
    F.contact |
    F.text.startswith('https://t.me/') |
    F.text.startswith('@')
)
async def got_correct_host(message: Message, state: FSMContext):
    host = {}
    if message.contact:
        host_telegram_id = message.contact.user_id
        host["telegram_id"] = host_telegram_id
        if host_telegram_id == message.from_user.id:
            host["username"] = message.from_user.username
    elif message.text.startswith('https://t.me/'):
        host["username"] = message.text.split('/')[-1]
    elif message.text.startswith('@'):
        host["username"] = message.text[1:]
    created_by = {
        "telegram_id": message.from_user.id,
        "username": message.from_user.username
    }
    data = await state.get_data()
    event = PydanticEvent(host=host, created_by=created_by, **data)
    try:
        response = await create_new_event(event)
        if response.status == 201:
            await message.answer(
                text=REGISTRATION_SUCCESS_TXT,
                reply_markup=ReplyKeyboardRemove()
            )
    except Exception:
        await message.answer(
            text=REGISTRATION_FAILED_TXT,
            reply_markup=ReplyKeyboardRemove()
        )
    await state.clear()


@router.message(
    EventRegistratorStates.wait_for_host
)
async def got_incorrect_host(message: Message):
    await message.answer(INCORRECT_HOST_TXT)
    return
