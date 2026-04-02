from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.database.instance import async_session
from src.database.actions import add_word, get_user_words, get_word_by_id, delete_word, update_word_status
from src.services.translator import translate_text
from src.keyboards.inline import get_add_word_confirm_kb, get_word_manage_kb, get_words_list_kb
from src.states import AddWord

router = Router()

# Показ списка "Мой словарь"
@router.message(F.text == "📖 Мой словарь")
async def show_dictionary(message: types.Message):
    async with async_session() as session:
        words = await get_user_words(session, message.from_user.id, "learning")
    
    print(f"[DEBUG] Показ словаря для {message.from_user.id}, найдено слов: {len(words)}")
    
    if not words:
        await message.answer("📖 В вашем словаре пока нет слов. \nЧтобы добавить слово, просто напишите его мне!")
        return

    await message.answer(
        "📖 Ваша библиотека слов (в процессе изучения). \nНажмите на слово, чтобы управлять им:",
        reply_markup=get_words_list_kb(words)
    )

# Показ меню управления конкретным словом
@router.callback_query(F.data.startswith("manage_word_"))
async def manage_word(callback: types.CallbackQuery):
    word_id = int(callback.data.split("_")[-1])
    async with async_session() as session:
        word = await get_word_by_id(session, word_id)
    
    if not word:
        await callback.answer("Слово не найдено!")
        return
    
    await callback.message.edit_text(
        f"Управление словом: <b>{word.original_text}</b> — <b>{word.translated_text}</b>",
        reply_markup=get_word_manage_kb(word.id, word.status)
    )
    await callback.answer()

# Изменение статуса (Выучил / Вернуть)
@router.callback_query(F.data.startswith("set_"))
async def change_status(callback: types.CallbackQuery):
    # data: set_learned_ID или set_learning_ID
    parts = callback.data.split("_")
    new_status = parts[1]
    word_id = int(parts[2])
    
    async with async_session() as session:
        await update_word_status(session, word_id, new_status)
    
    status_msg = "✅ Перенесено в 'Выученные'" if new_status == "learned" else "📖 Возвращено в 'Словарь'"
    await callback.message.edit_text(status_msg)
    await callback.answer()

# Удаление слова
@router.callback_query(F.data.startswith("delete_word_"))
async def handle_delete(callback: types.CallbackQuery):
    word_id = int(callback.data.split("_")[-1])
    
    async with async_session() as session:
        await delete_word(session, word_id)
    
    await callback.message.edit_text("🗑 Слово удалено из вашего словаря.")
    await callback.answer()

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
    
    await callback.message.edit_text(
        f"✅ Добавлено! <b>{data['original']}</b> — это <b>{data['translated']}</b>"
    )
    await state.clear()
    await callback.answer()

# Отмена добавления
@router.callback_query(F.data == "cancel_add")
async def cancel_add_word(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("❌ Добавление отменено.")
    await state.clear()
    await callback.answer()
