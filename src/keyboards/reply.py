from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from typing import Callable

def get_main_menu(_: Callable) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=_("menu_add_word"))],
            [KeyboardButton(text=_("menu_my_dictionary")), KeyboardButton(text=_("menu_training"))],
            [KeyboardButton(text=_("menu_learned")), KeyboardButton(text=_("menu_translator"))],
            [KeyboardButton(text=_("menu_settings"))]
        ],
        resize_keyboard=True
    )

def get_settings_menu(_: Callable) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=_("change_interface"))],
            [KeyboardButton(text=_("change_learning"))],
            [KeyboardButton(text=_("btn_back"))]
        ],
        resize_keyboard=True
    )

def get_learned_menu(_: Callable, total: int, week: int, today: int) -> ReplyKeyboardMarkup:
    # Key remains technical, but display depends on counts
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=_("menu_stats_all", total=total))],
            [KeyboardButton(text=_("menu_stats_week", week=week))],
            [KeyboardButton(text=_("menu_stats_today", today=today))],
            [KeyboardButton(text=_("btn_back"))]
        ],
        resize_keyboard=True
    )

def get_training_menu(_: Callable) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=_("menu_choose_translation"))],
            [KeyboardButton(text=_("btn_back"))]
        ],
        resize_keyboard=True
    )

def get_source_menu(_: Callable) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=_("menu_my_dictionary")), KeyboardButton(text=_("menu_learned"))],
            [KeyboardButton(text=_("btn_back"))]
        ],
        resize_keyboard=True
    )

def get_mode_menu(_: Callable) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=_("training_learn_native")), KeyboardButton(text=_("training_native_learn"))],
            [KeyboardButton(text=_("training_mix")), KeyboardButton(text=_("btn_back"))]
        ],
        resize_keyboard=True
    )

def get_quiz_keyboard(options: list[str], stop_text: str = "🛑 Завершить тренировку") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=options[0]), KeyboardButton(text=options[1])],
            [KeyboardButton(text=options[2]), KeyboardButton(text=options[3])],
            [KeyboardButton(text=stop_text)]
        ],
        resize_keyboard=True
    )

def get_back_button(_: Callable) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=_("btn_back"))]],
        resize_keyboard=True
    )

def get_translator_menu(_: Callable) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=_("menu_text_translation"))],
            [KeyboardButton(text=_("menu_photo_translation"))],
            [KeyboardButton(text=_("btn_back"))]
        ],
        resize_keyboard=True
    )

def get_lang_selection_keyboard(langs: list[tuple[str, str]]) -> ReplyKeyboardMarkup:
    """langs: list of (lang_code, lang_display_name)"""
    buttons = []
    for code, name in langs:
        buttons.append([KeyboardButton(text=name)])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
