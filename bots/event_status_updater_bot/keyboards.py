from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_confirm_reject_keyboard() -> InlineKeyboardBuilder:
    """
    Возвращает клавиатуру для подтверждения или отклонения мероприятия.
    """
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text='Подтвердить',
            callback_data='confirm'
        ),
        InlineKeyboardButton(
            text='Отклонить',
            callback_data='reject'
        )
    )
    return builder
