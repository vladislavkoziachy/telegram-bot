from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_add_word_confirm_kb():
    buttons = [
        [InlineKeyboardButton(text="🔊 Послушать", callback_data="pronounce_new")],
        [InlineKeyboardButton(text="✅ Добавить в словарь", callback_data="confirm_add")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_add")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_words_list_kb(words: list):
    # Генерируем список слов как кнопки
    builder = InlineKeyboardBuilder()
    for word in words:
        # При нажатии на слово отправим его ID, чтобы показать меню управления
        builder.row(InlineKeyboardButton(
            text=f"{word.original_text} — {word.translated_text}",
            callback_data=f"manage_word_{word.id}"
        ))
    return builder.as_markup()

def get_quiz_kb(options: list, word_id: int):
    """Генерирует кнопки с вариантами ответов."""
    builder = InlineKeyboardBuilder()
    for option in options:
        # callback_data будет содержать: answer_ПОДТВЕРЖДЕНИЕ_IDСЛОВА
        # Если это правильный ответ, пометим его 'correct'
        builder.row(InlineKeyboardButton(
            text=option['text'], 
            callback_data=f"quiz_{option['is_correct']}_{word_id}"
        ))
    return builder.as_markup()

def get_word_manage_kb(word_id: int, current_status: str):
    buttons = []
    buttons.append([InlineKeyboardButton(text="🔊 Послушать", callback_data=f"pronounce_word_{word_id}")])
    if current_status == "learning":
        buttons.append([InlineKeyboardButton(text="✅ Я выучил!", callback_data=f"set_learned_{word_id}")])
    else:
        buttons.append([InlineKeyboardButton(text="📖 Вернуть в словарь", callback_data=f"set_learning_{word_id}")])
        
    buttons.append([InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_word_{word_id}")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)
