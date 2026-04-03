import random
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from src.database.instance import async_session
from src.database.actions import (
    add_word, get_user_words, get_word_by_id, 
    delete_word, update_word_status, get_word_by_text
)
from src.services.translator import translate_text, is_russian
from src.services.voice import send_voice_pronunciation
from src.keyboards.inline import (
    get_add_word_confirm_kb, 
    get_paginated_words_kb, 
    get_word_manage_kb
)
from src.states import AddWord

router = Router()

# Показ списка "Мой словарь"
@router.message(F.text == "📖 Мой словарь")
async def show_dictionary(message: types.Message):
    await send_dict_page(message, 1)

async def send_dict_page(message: types.Message, page: int, is_edit: bool = False):
    user_id = message.chat.id
    async with async_session() as session:
        words = await get_user_words(session, user_id, "learning")
    
    if not words:
        await message.answer("📝 В вашем словаре пока нет слов. Напишите любое слово, чтобы добавить его!")
        return

    total_pages = (len(words) - 1) // 6 + 1
    kb = get_paginated_words_kb(words, page, total_pages, "dict")
    
    # Красивый заголовок в стиле старой версии
    text = f"📖 <b>Мой словарь (Всего: {len(words)})</b>\nСтраница: {page} из {total_pages}"
    
    if is_edit:
        await message.edit_text(text, reply_markup=kb)
    else:
        await message.answer(text, reply_markup=kb)

# Режим добавления слова (через кнопку)
@router.message(F.text == "➕ Добавить слово")
async def add_word_start(message: types.Message, state: FSMContext):
    await state.set_state(AddWord.waiting_for_word)
    await message.answer("Введите слово на английском или русском языке:")

# Обработка ввода слова (Универсальный перехватчик) - ВЫСОКИЙ ПРИОРИТЕТ
@router.message(
    F.text & ~F.text.startswith("/") & 
    ~F.text.in_([
        "🎓 Тренировка", "📖 Мой словарь", "📚 Выученные", "➕ Добавить слово", "⬅️ Назад в меню",
        "📊 Выученные за сегодняшний день", "📊 Выученные за эту неделю", "📊 Выученные за все время"
    ]),
    StateFilter(None, AddWord.waiting_for_word)
)
async def process_word_input(message: types.Message, state: FSMContext):
    res = await translate_text(message.text)
    
    if not res:
        await message.answer("🤔 Не удалось перевести это слово. Попробуйте другое!")
        return

    # Сохраняем во временное состояние
    await state.update_data(original=res['original'], translated=res['translated'])
    
    await message.answer(
        f"📝 Перевод: <b>{res['translated']}</b>\n\nДобавить в ваш словарь?",
        reply_markup=get_add_word_confirm_kb()
    )

# Озвучка слова из базы
@router.callback_query(F.data.startswith("pronounce_word:"))
async def pronounce_existing_word(callback: types.CallbackQuery):
    word_id = int(callback.data.split(":")[1])
    
    async with async_session() as session:
        word = await get_word_by_id(session, word_id)
    
    if not word:
        await callback.answer("Слово не найдено.")
        return

    text_to_speak = word.translated_text if is_russian(word.original_text) else word.original_text
    await send_voice_pronunciation(callback.message, text_to_speak)
    await callback.answer()

# Управление конкретным словом (меню)
@router.callback_query(F.data.startswith("manage_word:"))
async def show_word_management(callback: types.CallbackQuery):
    # Формат: manage_word:ID:PREFIX:PAGE
    parts = callback.data.split(":")
    word_id, prefix, page = int(parts[1]), parts[2], int(parts[3])

    async with async_session() as session:
        word = await get_word_by_id(session, word_id)
    
    if not word:
        await callback.answer("Слово не найдено.")
        return

    # Заголовок управления словом (EN - RU)
    title = f"{word.translated_text} — {word.original_text}" if is_russian(word.original_text) else f"{word.original_text} — {word.translated_text}"
    text = f"🔤 <b>Слово:</b> {title}"
    
    await callback.message.edit_text(
        text, 
        reply_markup=get_word_manage_kb(word.id, word.status, prefix, page)
    )
    await callback.answer()

# Изменение статуса
@router.callback_query(F.data.startswith("set_learned:") | F.data.startswith("set_learning:"))
async def change_status(callback: types.CallbackQuery):
    parts = callback.data.split(":")
    new_status, word_id = parts[0].replace("set_", ""), int(parts[1])
    
    async with async_session() as session:
        await update_word_status(session, word_id, new_status)
        await session.commit()
    
    msg = "✅ Перенесено в 'Выученные'" if new_status == "learned" else "📖 Возвращено в 'Словарь'"
    await callback.message.edit_text(msg)
    await callback.answer()

# Удаление слова
@router.callback_query(F.data.startswith("delete_word:"))
async def handle_delete(callback: types.CallbackQuery):
    word_id = int(callback.data.split(":")[1])
    
    async with async_session() as session:
        await delete_word(session, word_id)
        await session.commit()
    
    await callback.message.edit_text("🗑 Слово удалено.")
    await callback.answer()

# Озвучка нового слова
@router.callback_query(F.data == "pronounce_new")
async def pronounce_new_word(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data:
        await callback.answer("Ошибка: данные не найдены.")
        return
    
    text_to_speak = data['translated'] if is_russian(data['original']) else data['original']
    await send_voice_pronunciation(callback.message, text_to_speak)
    await callback.answer()

# Отмена добавления
@router.callback_query(F.data == "cancel_add")
async def cancel_add_word(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("❌ Добавление отменено.")
    await state.clear()
    await callback.answer()

# Подтверждение добавления
@router.callback_query(F.data == "confirm_add")
async def confirm_add_word(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = callback.from_user.id
    original = data['original']
    
    async with async_session() as session:
        # Проверка на дубликаты
        existing_word = await get_word_by_text(session, user_id, original)
        if existing_word:
            status_text = "в словаре" if existing_word.status == "learning" else "в списке выученных"
            await callback.message.edit_text(f"⚠️ Слово <b>{original}</b> уже есть {status_text}!")
            await state.clear()
            await callback.answer()
            return
            
        await add_word(session, user_id, original, data['translated'])
        await session.commit()
    
    await callback.message.edit_text(f"✅ Добавлено! <b>{data['original']}</b> — это <b>{data['translated']}</b>")
    await state.clear()
    await callback.answer()
