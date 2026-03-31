from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_learned_menu():
    # Создаем кнопки под сообщением (Inline)
    buttons = [
        [InlineKeyboardButton(text="📅 Сегодня", callback_data="learned_today")],
        [InlineKeyboardButton(text="📅 За неделю", callback_data="learned_week")],
        [InlineKeyboardButton(text="📅 За всё время", callback_data="learned_all")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
