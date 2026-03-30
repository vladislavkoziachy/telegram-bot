from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from typing import Callable

from src.database import get_user, update_user, create_user
from src.keyboards.reply import get_main_menu, get_settings_menu, get_lang_selection_keyboard, get_back_button
from src.states import LanguageStates

router = Router()

LANGS_INTERFACE = [
    ("ru", "Русский 🇷🇺"),
    ("uk", "Українська 🇺🇦"),
    ("pl", "Polski 🇵🇱")
]

LANGS_LEARNING = [
    ("en", "English 🇬🇧"),
    ("pl", "Polski 🇵🇱"),
    ("es", "Español 🇪🇸")
]

@router.message(F.text == "⚙️ Настройки") # This might need a better trigger or i18n trigger
@router.message(F.text.in_(["⚙️ Настройки", "⚙️ Налаштування", "⚙️ Ustawienia"]))
async def btn_settings(message: Message, _: Callable, user_lang: str, learn_lang: str):
    text = _("settings_text", int_lang=user_lang.upper(), learn_lang=learn_lang.upper())
    await message.answer(text, reply_markup=get_settings_menu(_))

@router.message(F.text.in_(["Сменить язык интерфейса", "Змінити мову інтерфейсу", "Zmień język interfejsu"]))
async def btn_change_interface(message: Message, state: FSMContext, _: Callable):
    await state.set_state(LanguageStates.waiting_for_interface_lang)
    await message.answer(_("welcome_interface"), reply_markup=get_lang_selection_keyboard(LANGS_INTERFACE))

@router.message(LanguageStates.waiting_for_interface_lang)
async def process_interface_lang(message: Message, state: FSMContext, _: Callable):
    lang_code = None
    for code, name in LANGS_INTERFACE:
        if message.text == name:
            lang_code = code
            break
    
    if not lang_code:
        await message.answer("Пожалуйста, выберите язык из списка / Будь ласка, виберіть мову зі списку / Proszę wybrać język z listy")
        return

    await update_user(message.from_user.id, interface_lang=lang_code)
    
    # We need to refresh the "_" function with the new language for the next message
    from src.services.i18n import _ as get_text_new
    new_text = lambda key, **kwargs: get_text_new(key, lang_code, **kwargs)
    
    await state.set_state(LanguageStates.waiting_for_learning_lang)
    await message.answer(new_text("welcome_learning"), reply_markup=get_lang_selection_keyboard(LANGS_LEARNING))

@router.message(F.text.in_(["Сменить язык обучения", "Змінити мову навчання", "Zmień język nauki"]))
async def btn_change_learning(message: Message, state: FSMContext, _: Callable):
    await state.set_state(LanguageStates.waiting_for_learning_lang)
    await message.answer(_("welcome_learning"), reply_markup=get_lang_selection_keyboard(LANGS_LEARNING))

@router.message(LanguageStates.waiting_for_learning_lang)
async def process_learning_lang(message: Message, state: FSMContext, _: Callable):
    lang_code = None
    for code, name in LANGS_LEARNING:
        if message.text == name:
            lang_code = code
            break
    
    if not lang_code:
        await message.answer(_("welcome_learning"))
        return

    await update_user(message.from_user.id, learning_lang=lang_code)
    await state.clear()
    await message.answer(_("main_menu_text"), reply_markup=get_main_menu(_))
