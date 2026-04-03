from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.database.instance import async_session
from src.database.actions import add_word, get_user_words, get_word_by_id, delete_word, update_word_status
from src.services.translator import translate_text, is_russian
from src.services.voice import send_voice_pronunciation
from src.keyboards.inline import (
    get_add_word_confirm_kb, 
    get_words_list_kb, 
    get_word_manage_kb
)
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
@router.message(F.text & ~F.text.startswith("/") & ~F.text.in_([
    "➕ Добавить слово", "📖 Мой словарь", "📚 Выученные", "🎓 Тренировка", "⬅️ Назад в меню"
]))
async def process_word_input(message: types.Message, state: FSMContext):
    word = message.text.strip()
    
    # Пытаемся перевести слово
    res = translate_text(word)
    
    if not res:
        await message.answer("🤔 Не удалось перевести это слово. Попробуйте другое!")
        return

    # Сохраняем во временное состояние для подтверждения
    await state.update_data(original=res['original'], translated=res['translated'])
    
    await message.answer(
        f"📝 Перевод: <b>{res['translated']}</b>\n\nДобавить в ваш словарь?",
        reply_markup=get_add_word_confirm_kb()
    )

# Озвучка нового слова (которое еще не в базе)
@router.callback_query(F.data == "pronounce_new")
async def pronounce_new_word(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data:
        await callback.answer("Ошибка: данные не найдены.")
        return
    
    # Решаем, что озвучить (английскую версию)
    text_to_speak = data['translated'] if is_russian(data['original']) else data['original']
    
    await send_voice_pronunciation(callback.message, text_to_speak)
    await callback.answer()

# Озвучка слова из базы
@router.callback_query(F.data.startswith("pronounce_word_"))
async def pronounce_existing_word(callback: types.CallbackQuery):
    word_id = int(callback.data.split("_")[-1])
    
    async with async_session() as session:
        word = await get_word_by_id(session, word_id)
    
    if not word:
        await callback.answer("Слово не найдено.")
        return

    # Решаем, что озвучить (английскую версию)
    text_to_speak = word.translated_text if is_russian(word.original_text) else word.original_text
    
    await send_voice_pronunciation(callback.message, text_to_speak)
    await callback.answer()

# Управление конкретным словом (показ меню)
@router.callback_query(F.data.startswith("manage_word_"))
async def show_word_management(callback: types.CallbackQuery):
    # Формат: manage_word_ID_PERIOD_PAGE или просто manage_word_ID
    parts = callback.data.split("_")
    word_id = int(parts[2])
    
    period = parts[3] if len(parts) > 3 else None
    page = int(parts[4]) if len(parts) > 4 else 1

    async with async_session() as session:
        word = await get_word_by_id(session, word_id)
    
    if not word:
        await callback.answer("Слово не найдено.")
        return

    text = f"🔤 <b>Слово:</b> {word.original_text}\n📝 <b>Перевод:</b> {word.translated_text}"
    
    await callback.message.edit_text(
        text, 
        reply_markup=get_word_manage_kb(word.id, word.status, period, page)
    )
    await callback.answer()

# Отмена добавления
@router.callback_query(F.data == "cancel_add")
async def cancel_add_word(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("❌ Добавление отменено.")
    await state.clear()
    await callback.answer()

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
    await state.clear()
    await callback.answer()
