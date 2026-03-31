from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from typing import Callable

from src.keyboards.reply import get_translator_menu, get_main_menu, get_back_button
from src.states import TranslatorStates
from src.services.translator import translate_full_text

router = Router()

@router.message(F.text.in_(["🌐 Переводчик", "🌐 Перекладач", "🌐 Tłumacz"]))
async def btn_translator_menu(message: Message, state: FSMContext, _: Callable):
    await state.clear()
    await message.answer(_("menu_translator"), reply_markup=get_translator_menu(_))

@router.message(F.text.in_(["📝 Перевод текста", "📝 Переклад тексту", "📝 Tłumaczenie tekstu"]))
async def btn_text_translation(message: Message, state: FSMContext, _: Callable):
    await state.set_state(TranslatorStates.waiting_for_text)
    await message.answer(_("translator_prompt", default="Пожалуйста, отправьте текст для перевода..."), reply_markup=get_back_button(_))

@router.message(TranslatorStates.waiting_for_text)
async def process_text_translation(message: Message, state: FSMContext, _: Callable, learn_lang: str):
    text = message.text
    
    if text in ["⬅️ Назад", "⬅️ Взад", "⬅️ Wstecz"]:
        await state.clear()
        await message.answer(_("menu_translator"), reply_markup=get_translator_menu(_))
        return

    await message.answer("⏳")
    result = translate_full_text(text, target_lang=learn_lang)
    
    await message.answer(f"✅:\n\n{result}", reply_markup=get_back_button(_))
