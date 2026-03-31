from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Добавить слово")],
            [KeyboardButton(text="📖 Мой словарь"), KeyboardButton(text="🎯 Тренировка")],
            [KeyboardButton(text="📚 Выученные"), KeyboardButton(text="🌐 Переводчик")],
            [KeyboardButton(text="⚙️ Настройки")]
        ],
        resize_keyboard=True
    )

def get_settings_menu() -> ReplyKeyboardMarkup:
    # We removed language changes, but kept the menu for structure/stats
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Моя статистика")],
            [KeyboardButton(text="⬅️ Назад")]
        ],
        resize_keyboard=True
    )

def get_learned_menu(total: int, week: int, today: int) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=f"📚 Все выученные ({total})")],
            [KeyboardButton(text=f"📅 За неделю ({week})")],
            [KeyboardButton(text=f"🕒 За сегодня ({today})")],
            [KeyboardButton(text="⬅️ Назад")]
        ],
        resize_keyboard=True
    )

def get_training_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🧩 Выбери перевод")],
            [KeyboardButton(text="⬅️ Назад")]
        ],
        resize_keyboard=True
    )

def get_source_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📖 Мой словарь"), KeyboardButton(text="📚 Выученные")],
            [KeyboardButton(text="⬅️ Назад")]
        ],
        resize_keyboard=True
    )

def get_mode_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="EN → RU"), KeyboardButton(text="RU → EN")],
            [KeyboardButton(text="MIX"), KeyboardButton(text="⬅️ Назад")]
        ],
        resize_keyboard=True
    )

def get_quiz_keyboard(options: list[str], stop_text: str = "⬅️ Назад") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=options[0]), KeyboardButton(text=options[1])],
            [KeyboardButton(text=options[2]), KeyboardButton(text=options[3])],
            [KeyboardButton(text=stop_text)]
        ],
        resize_keyboard=True
    )

def get_back_button() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⬅️ Назад")]],
        resize_keyboard=True
    )

def get_translator_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Текстовый перевод")],
            [KeyboardButton(text="⬅️ Назад")]
        ],
        resize_keyboard=True
    )
