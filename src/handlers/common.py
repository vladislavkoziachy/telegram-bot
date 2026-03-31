from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from src.keyboards.reply import get_main_menu
from src.services.translator import translate_word
from src.keyboards.inline import get_add_word_keyboard
from src.database import get_user, create_user

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user = await get_user(message.from_user.id)
    if not user:
        # Default to RU interface and EN learning
        await create_user(message.from_user.id, interface_lang="ru", learning_lang="en")
        
    await message.answer("Главное меню 👇", reply_markup=get_main_menu())

@router.message(F.text == "⬅️ Назад")
async def btn_back(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню 👇", reply_markup=get_main_menu())

# Fallback for translating random text sent in the main menu
@router.message(F.text)
async def translate_any_text(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        return # Let other handlers deal with it
        
    text = message.text
    
    ignored_texts = [
        "➕ Добавить слово", "📖 Мой словарь", "🎯 Тренировка", 
        "📚 Выученные", "🌐 Переводчик", "⚙️ Настройки"
    ]
    
    if text.startswith("/") or text in ignored_texts:
        return # Should have been caught by other routers, but just in case
        
    word_learn, word_native = translate_word(text)
    keyboard = get_add_word_keyboard(word_learn, word_native)
    await message.answer(f"🇬🇧 {word_learn} \n🇷🇺 {word_native}", reply_markup=keyboard)
