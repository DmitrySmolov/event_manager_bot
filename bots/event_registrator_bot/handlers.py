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
PROMPT_SHARE_HOST_TXT = (
    'Спасибо!\n\n'
    'Теперь нам нужно узнать, кто будет ведущим мероприятия.\n'
    'Если им будете вы, то нажмите на кнопку "Отправить мой контакт".\n'
    'Либо прикрепите контакт другого пользователя Телеграм и отправьте '
    'сообщение.'
)
PROMPT_ENTER_HOST_USERNAME_TXT = (
    'Спасибо, что полелились контактом пользователя {name}.\n\n'
    'Укажите, пожалуйста, username этого пользователя в Телеграме.'
)
INCORRECT_HOST_USERNAME_TXT = (
    'Для ведущего мероприятия необходимо указать username пользователя.\n'
    'Попробуйте ещё раз.'
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
INCORRECT_HOST_CONTACT_TXT = (
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
    wait_for_host_contact = State()
    wait_for_host_username = State()


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
        EventRegistratorStates.wait_for_host_contact.state,
        EventRegistratorStates.wait_for_host_username.state
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
        text=PROMPT_SHARE_HOST_TXT,
        reply_markup=SEND_MY_CONTACT_KBOARD
    )
    await state.set_state(EventRegistratorStates.wait_for_host_contact)


@router.message(
    EventRegistratorStates.wait_for_location
)
async def got_incorrect_location(message: Message):
    await message.answer(INCORRECT_LOCATION_TXT)
    return


@router.message(
    EventRegistratorStates.wait_for_host_contact,
    F.contact |
    F.text.startswith('https://t.me/') |
    F.text.startswith('@')
)
async def got_correct_host_contact(message: Message, state: FSMContext):
    host = {}
    if message.contact:
        host_telegram_id = message.contact.user_id
        host["telegram_id"] = host_telegram_id
        if host_telegram_id == message.from_user.id:
            host["username"] = message.from_user.username
        else:
            await state.update_data(host=host)
            name = message.contact.first_name
            await message.answer(
                text=PROMPT_ENTER_HOST_USERNAME_TXT.format(name=name),
                reply_markup=ReplyKeyboardRemove()
            )
            return await state.set_state(
                EventRegistratorStates.wait_for_host_username
            )
    elif message.text.startswith('https://t.me/'):
        host["username"] = message.text.split('/')[-1]
    elif message.text.startswith('@'):
        host["username"] = message.text[1:]
    await state.update_data(host=host)
    return await _got_all_data(message, state)


@router.message(
    EventRegistratorStates.wait_for_host_contact
)
async def got_incorrect_host_contact(message: Message):
    await message.answer(INCORRECT_HOST_CONTACT_TXT)
    return


@router.message(
    EventRegistratorStates.wait_for_host_username,
    F.text
)
async def got_correct_host_username(message: Message, state: FSMContext):
    data = await state.get_data()
    host = data.get("host", {})
    host["username"] = message.text
    await state.update_data(host=host)
    return await _got_all_data(message, state)


@router.message(
    EventRegistratorStates.wait_for_host_username
)
async def got_incorrect_host_username(message: Message):
    await message.answer(INCORRECT_HOST_USERNAME_TXT)
    return


async def _got_all_data(message: Message, state: FSMContext):
    data = await state.get_data()
    created_by = {
        "telegram_id": message.from_user.id,
        "username": message.from_user.username
    }
    event = PydanticEvent(created_by=created_by, **data)
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
