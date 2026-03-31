import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from src.keyboards.reply import get_translator_menu, get_main_menu, get_back_button
from src.states import TranslatorStates
from src.services.translator import translate_full_text

router = Router()
logger = logging.getLogger(__name__)

MAIN_MENU_BUTTONS = ["➕ Добавить слово", "📖 Мой словарь", "🎯 Тренировка", "📚 Выученные", "🌐 Переводчик", "⚙️ Настройки"]

@router.message(F.text == "🌐 Переводчик")
async def btn_translator_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Раздел переводчика 🌐", reply_markup=get_translator_menu())

@router.message(F.text == "📝 Текстовый перевод")
async def btn_text_translation(message: Message, state: FSMContext):
    await state.set_state(TranslatorStates.waiting_for_text)
    await message.answer("Пришлите любой текст для перевода... ✍️", reply_markup=get_back_button())

@router.message(TranslatorStates.waiting_for_text)
async def process_text_translation(message: Message, state: FSMContext):
    text = message.text
    logger.info(f"User {message.from_user.id} in TranslatorStates: {text}")
    
    if text == "⬅️ Назад":
        await state.clear()
        await message.answer("Раздел переводчика 🌐", reply_markup=get_translator_menu())
        return

    if text in MAIN_MENU_BUTTONS:
        await state.clear()
        await message.answer("Переводчик закрыт. Переходим в другой раздел... 🔄")
        return

    # Translate to English by default for learning purposes
    result = translate_full_text(text, target_lang="en")
    
    await message.answer(f"Результат перевода:\n\n{result}", reply_markup=get_back_button())
