from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_add_word_confirm_kb():
    buttons = [
        [InlineKeyboardButton(text="🔊 Послушать", callback_data="pronounce_new")],
        [InlineKeyboardButton(text="✅ Добавить в словарь", callback_data="confirm_add")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_add")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_quiz_kb(options: list, word_id: int):
    """Генерирует кнопки с вариантами ответов + кнопку выхода."""
    builder = InlineKeyboardBuilder()
    for option in options:
        builder.row(InlineKeyboardButton(
            text=option['text'], 
            callback_data=f"quiz_{option['is_correct']}_{word_id}"
        ))
    # Пятая кнопка - выход в меню
    builder.row(InlineKeyboardButton(text="🏠 В меню", callback_data="train_stop"))
    return builder.as_markup()

def get_paginated_words_kb(words: list, page: int, total_pages: int, prefix: str):
    """Генерирует список слов с кнопками пагинации (универсальная)."""
    builder = InlineKeyboardBuilder()
    
    # Показываем по 6 слов на странице
    start = (page - 1) * 6
    end = start + 6
    page_words = words[start:end]

    for word in page_words:
        # Решаем, какой язык ставить первым (английский — первый)
        from src.services.translator import is_russian
        if is_russian(word.original_text):
            button_text = f"{word.translated_text} — {word.original_text}"
        else:
            button_text = f"{word.original_text} — {word.translated_text}"
            
        builder.row(InlineKeyboardButton(
            text=button_text,
            callback_data=f"manage_word:{word.id}:{prefix}:{page}" 
        ))

    # Кнопки навигации
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Пред.", callback_data=f"page:{page-1}:{prefix}"))
    
    nav_buttons.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="ignore"))

    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton(text="След. ➡️", callback_data=f"page:{page+1}:{prefix}"))
    
    if nav_buttons:
        builder.row(*nav_buttons)
        
    return builder.as_markup()

def get_word_manage_kb(word_id: int, current_status: str, back_prefix: str = None, back_page: int = 1):
    buttons = []
    buttons.append([InlineKeyboardButton(text="🔊 Прослушать", callback_data=f"pronounce_word:{word_id}")])
    
    if current_status == "learning":
        buttons.append([InlineKeyboardButton(text="✅ Я выучил!", callback_data=f"set_learned:{word_id}")])
    else:
        buttons.append([InlineKeyboardButton(text="📖 Вернуть в словарь", callback_data=f"set_learning:{word_id}")])
    
    # Кнопка удаления
    buttons.append([InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_word:{word_id}")])
    
    # Кнопка возврата к списку
    if back_prefix:
        buttons.append([InlineKeyboardButton(text="🔙 Назад к списку", callback_data=f"page:{back_page}:{back_prefix}")])
        
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_training_type_kb():
    buttons = [
        [InlineKeyboardButton(text="💎 Выбери перевод", callback_data="train_type_choice")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_training_pool_kb():
    buttons = [
        [InlineKeyboardButton(text="📖 Учить новые (Словарь)", callback_data="train_pool_learning")],
        [InlineKeyboardButton(text="✅ Повторить выученные", callback_data="train_pool_learned")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_training_direction_kb():
    buttons = [
        [InlineKeyboardButton(text="🇷🇺 RU ➡️ 🇬🇧 EN", callback_data="train_dir_ru_en")],
        [InlineKeyboardButton(text="🇬🇧 EN ➡️ 🇷🇺 RU", callback_data="train_dir_en_ru")],
        [InlineKeyboardButton(text="🔀 Микс (Случайно)", callback_data="train_dir_mix")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
