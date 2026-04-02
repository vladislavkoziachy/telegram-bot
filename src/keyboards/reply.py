from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_main_menu():
    keyboard = [
        [KeyboardButton(text="🎓 Тренировка")],
        [KeyboardButton(text="➕ Добавить слово")],
        [KeyboardButton(text="📖 Мой словарь"), KeyboardButton(text="📚 Выученные")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_learned_menu(counts: dict):
    # counts = {"today": 0, "week": 0, "all": 0}
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text=f"📅 Выучено за сегодня ({counts['today']})"))
    builder.row(KeyboardButton(text=f"📅 Выучено за неделю ({counts['week']})"))
    builder.row(KeyboardButton(text=f"📅 Выучено за всё время ({counts['all']})"))
    builder.row(KeyboardButton(text="⬅️ Назад в меню"))
    
    return builder.as_markup(resize_keyboard=True)
