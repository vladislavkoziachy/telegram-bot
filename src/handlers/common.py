from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from src.keyboards.reply import get_main_menu, get_lang_selection_keyboard
from src.services.translator import translate_word, FLAGS
from src.keyboards.inline import get_add_word_keyboard
from src.database import get_user, create_user
from src.states import LanguageStates
from src.services.i18n import get_all_translated
from typing import Callable

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext, _: Callable):
    await state.clear()
    user = await get_user(message.from_user.id)
    if not user:
        from src.handlers.settings import LANGS_INTERFACE
        await state.set_state(LanguageStates.waiting_for_interface_lang)
        await message.answer(
            "🇷🇺 Выберите язык интерфейса:\n"
            "🇺🇦 Виберіть мову інтерфейсу:\n"
            "🇵🇱 Wybierz język interfejsu:", 
            reply_markup=get_lang_selection_keyboard(LANGS_INTERFACE)
        )
        return

    await message.answer(_("main_menu_text"), reply_markup=get_main_menu(_))

@router.message(F.text.in_(["⬅️ Назад", "⬅️ Взад", "⬅️ Wstecz"]))
async def btn_back(message: Message, state: FSMContext, _: Callable):
    await state.clear()
    await message.answer(_("main_menu_text"), reply_markup=get_main_menu(_))

# Fallback for translating random text sent in the main menu
@router.message(F.text)
async def translate_any_text(message: Message, state: FSMContext, _: Callable, user_lang: str, learn_lang: str):
    current_state = await state.get_state()
    if current_state is not None:
        return # Let other handlers deal with it
        
    text = message.text
    
    ignored_texts = (
        get_all_translated("menu_add_word") +
        get_all_translated("menu_my_dictionary") +
        get_all_translated("menu_training") +
        get_all_translated("menu_learned") +
        get_all_translated("menu_translator") +
        get_all_translated("menu_settings")
    )
    
    if text.startswith("/") or text in ignored_texts:
        return # Should have been caught by other routers, but just in case
        
    # Also ignore texts from other languages if we had them in a list, 
    # but for now we'll just try to translate
    
    word_learn, word_native = translate_word(text, user_lang=user_lang, learn_lang=learn_lang)
    keyboard = get_add_word_keyboard(_, word_learn, word_native)
    flag_learn = FLAGS.get(learn_lang, "")
    flag_native = FLAGS.get(user_lang, "")
    await message.answer(f"{flag_learn} {word_learn} \n{flag_native} {word_native}", reply_markup=keyboard)
