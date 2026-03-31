from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu():
    # Создаем список кнопок. Каждая строка списка — это ряд кнопок в Telegram.
    keyboard = [
        [KeyboardButton(text="➕ Добавить слово")],
        [KeyboardButton(text="📖 Мой словарь"), KeyboardButton(text="📚 Выученные")]
    ]
    
    # resize_keyboard=True делает кнопки маленькими и аккуратными
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие... 👇"
    )
