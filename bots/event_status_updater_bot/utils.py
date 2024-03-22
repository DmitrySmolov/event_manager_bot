from aiogram import Bot


async def delete_inline_markup(
        bot: Bot,
        chat_id: int,
        message_id: int
):
    """
    Удаляет inline клавиатуру у сообщения.
    """
    await bot.edit_message_reply_markup(
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=None
    )
