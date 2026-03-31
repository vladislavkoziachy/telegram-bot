from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_add_word_confirm_kb():
    buttons = [
        [InlineKeyboardButton(text="✅ Добавить в словарь", callback_data="confirm_add")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_add")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_word_manage_kb(word_id: int, current_status: str):
    buttons = []
    if current_status == "learning":
        buttons.append([InlineKeyboardButton(text="✅ Я выучил!", callback_data=f"set_learned_{word_id}")])
    else:
        buttons.append([InlineKeyboardButton(text="📖 Вернуть в словарь", callback_data=f"set_learning_{word_id}")])
        
    buttons.append([InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_word_{word_id}")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)
