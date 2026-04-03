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
    builder.row(KeyboardButton(text=f"📊 Выученные за сегодняшний день ({counts['today']})"))
    builder.row(KeyboardButton(text=f"📊 Выученные за эту неделю ({counts['week']})"))
    builder.row(KeyboardButton(text=f"📊 Выученные за все время ({counts['all']})"))
    builder.row(KeyboardButton(text="⬅️ Назад в меню"))
    
    return builder.as_markup(resize_keyboard=True)
def get_training_quiz_reply_kb(options: list):
    """Генерирует Reply-кнопки с вариантами ответов (нижнее меню)."""
    builder = ReplyKeyboardBuilder()
    
    # Добавляем 4 варианта (по 2 в ряд)
    for option in options:
        builder.add(KeyboardButton(text=option['text']))
    
    builder.adjust(2) # Делаем сетку 2x2
    
    # Кнопка выхода в самом низу отдельным рядом
    builder.row(KeyboardButton(text="🏠 В меню"))
    
    return builder.as_markup(resize_keyboard=True)
