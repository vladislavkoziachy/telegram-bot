from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from typing import Callable

from src.database import get_user, update_user, create_user
from src.keyboards.reply import get_main_menu, get_settings_menu, get_lang_selection_keyboard
from src.states import LanguageStates
from src.services.i18n import get_all_translated

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


@router.message(F.text.in_(get_all_translated("menu_settings")))
async def btn_settings(message: Message, _: Callable, user_lang: str, learn_lang: str):
    text = _("settings_text", int_lang=user_lang.upper(), learn_lang=learn_lang.upper())
    await message.answer(text, reply_markup=get_settings_menu(_))

@router.message(F.text.in_(get_all_translated("change_interface")))
async def btn_change_interface(message: Message, state: FSMContext, _: Callable):
    await state.set_state(LanguageStates.waiting_for_interface_lang)
    await message.answer(_("select_interface_lang", default="На какой язык хотите сменить интерфейс?"), reply_markup=get_lang_selection_keyboard(LANGS_INTERFACE))

@router.message(LanguageStates.waiting_for_interface_lang)
async def process_interface_lang(message: Message, state: FSMContext, _: Callable):
    lang_code = None
    for code, name in LANGS_INTERFACE:
        if message.text == name:
            lang_code = code
            break
    
    if not lang_code:
        await message.answer(
            "🇷🇺 Пожалуйста, выберите язык из списка:\n"
            "🇺🇦 Будь ласка, виберіть мову зі списку:\n"
            "🇵🇱 Proszę wybrać język z listy:"
        )
        return

    user = await get_user(message.from_user.id)
    if not user:
        await create_user(message.from_user.id, interface_lang=lang_code)
        # after creation, we don't have user.learning_lang object immediately, let's fix it:
        u_learning_lang = "en"
    else:
        await update_user(message.from_user.id, interface_lang=lang_code)
        u_learning_lang = user.learning_lang
        
    # We need to refresh the "_" function with the new language for the next message
    from src.services.i18n import _ as get_text_new
    new_text = lambda key, **kwargs: get_text_new(key, lang_code, **kwargs)
    
    await state.clear()
    text = new_text("settings_text", int_lang=lang_code.upper(), learn_lang=u_learning_lang.upper())
    await message.answer(text, reply_markup=get_settings_menu(new_text))

@router.message(F.text.in_(get_all_translated("change_learning")))
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
