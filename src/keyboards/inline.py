from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Callable

def get_add_word_keyboard(_: Callable, word_learn: str, word_native: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔊 " + _("pronunciation", default="Произношение"), callback_data=f"voice:{word_learn}")],
        [InlineKeyboardButton(text="➕ " + _("add_to_dictionary", default="Добавить в словарь"), callback_data=f"add:{word_learn}:{word_native}")]
    ])

def get_dictionary_keyboard(_: Callable, words: list, page: int = 0, per_page: int = 10, prefix="dic") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    start_idx = page * per_page
    end_idx = start_idx + per_page
    page_words = words[start_idx:end_idx]
    
    for word_obj in page_words:
        safe_word = word_obj.word[:20]
        builder.button(text=f"{word_obj.word} — {word_obj.translation}", callback_data=f"word:{prefix}:{safe_word}")
    
    builder.adjust(1) # One button per row for words
    
    # Pagination row
    if page > 0 or end_idx < len(words):
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton(text=_("btn_back"), callback_data=f"{prefix}_page:{page-1}"))
        else:
            nav_buttons.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
            
        nav_buttons.append(InlineKeyboardButton(text=str(page+1), callback_data="ignore"))
        
        if end_idx < len(words):
            nav_buttons.append(InlineKeyboardButton(text=_("btn_forward", default="Вперед ➡️"), callback_data=f"{prefix}_page:{page+1}"))
        else:
            nav_buttons.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
            
        builder.row(*nav_buttons)
        
    return builder.as_markup()

def get_word_action_keyboard(_: Callable, word: str, prefix: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔊 " + _("pronunciation", default="Произношение"), callback_data=f"voice:{word}")],
        [InlineKeyboardButton(text="✅ " + _("learned_action", default="Выучил"), callback_data=f"learn:{prefix}:{word}")],
        [InlineKeyboardButton(text="❌ " + _("delete_action", default="Удалить"), callback_data=f"delete:{prefix}:{word}")],
        [InlineKeyboardButton(text=_("btn_back_list", default="⬅️ Назад к списку"), callback_data=f"back_list:{prefix}")]
    ])

def get_learned_word_action_keyboard(_: Callable, word: str, prefix: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔊 " + _("pronunciation", default="Произношение"), callback_data=f"voice:{word}")],
        [InlineKeyboardButton(text="↩️ " + _("unlearn_action", default="Вернуть в словарь"), callback_data=f"unlearn:{prefix}:{word}")],
        [InlineKeyboardButton(text=_("btn_back_list", default="⬅️ Назад к списку"), callback_data=f"back_list:{prefix}")]
    ])
