from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.database.instance import async_session
from src.database.actions import add_word, get_user_words
from src.services.translator import translate_text
from src.keyboards.inline import get_add_word_confirm_kb, get_word_manage_kb
from src.states import AddWord

router = Router()

# Обработка любого текста — если бот в режиме "Добавить слово"
@router.message(AddWord.waiting_for_word)
async def process_word_input(message: types.Message, state: FSMContext):
    # Если нажали кнопку меню — отменяем ввод
    if message.text.startswith("➕") or message.text.startswith("📖") or message.text.startswith("📚"):
        await state.clear()
        return

    # Переводим слово
    result = translate_text(message.text)
    if not result:
        await message.answer("Извините, не удалось перевести слово. Попробуйте другое.")
        return

    # Сохраняем в память для подтверждения
    await state.update_data(
        original=result['original'],
        translated=result['translated']
    )
    
    await message.answer(
        f"🔍 Перевод: <b>{result['translated']}</b>\n\nДобавить это слово в ваш словарь?",
        reply_markup=get_add_word_confirm_kb()
    )

# Подтверждение добавления (через Inline кнопку)
@router.callback_query(F.data == "confirm_add")
async def confirm_add_word(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    async with async_session() as session:
        await add_word(session, callback.from_user.id, data['original'], data['translated'])
    
    await callback.message.edit_text(f"✅ Слово '<b>{data['original']}</b>' добавлено!")
    await state.clear()
    await callback.answer()

# Отмена добавления
@router.callback_query(F.data == "cancel_add")
async def cancel_add_word(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("❌ Добавление отменено.")
    await state.clear()
    await callback.answer()
