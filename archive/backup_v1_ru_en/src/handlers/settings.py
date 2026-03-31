import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from src.database import get_user, count_words
from src.keyboards.reply import get_main_menu, get_settings_menu

router = Router()
logger = logging.getLogger(__name__)

@router.message(F.text == "⚙️ Настройки")
async def btn_settings(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Раздел настроек и статистики ⚙️", reply_markup=get_settings_menu())

@router.message(F.text == "📊 Моя статистика")
async def btn_stats(message: Message, state: FSMContext):
    user_id = message.from_user.id
    logger.info(f"User {user_id} requested stats")
    
    # Simple stats for English learning
    learning_count = await count_words(user_id, "en", "learning")
    learned_count = await count_words(user_id, "en", "learned")
    
    text = (
        "📊 Твоя статистика (English):\n\n"
        f"📖 Слов в словаре: {learning_count}\n"
        f"✅ Выучено слов: {learned_count}\n"
        f"🎯 Всего добавлено: {learning_count + learned_count}"
    )
    await message.answer(text, reply_markup=get_settings_menu())
