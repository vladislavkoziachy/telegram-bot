import random
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from src.database.instance import async_session
from src.database.actions import add_word, get_user_words, get_word_by_id, delete_word, update_word_status
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

    total_pages = (len(words) - 1) // 10 + 1
    kb = get_paginated_words_kb(words, page, total_pages, "dict")
    
    text = f"📖 <b>Ваш словарь (в процессе изучения)</b>\nСтраница: {page} из {total_pages}"
    
    if is_edit:
        await message.edit_text(text, reply_markup=kb)
    else:
        await message.answer(text, reply_markup=kb)

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

# Управление конкретным словом (показ меню)
@router.callback_query(F.data.startswith("manage_word:"))
async def show_word_management(callback: types.CallbackQuery):
    # Формат: manage_word:ID:PREFIX:PAGE
    parts = callback.data.split(":")
    
    if len(parts) < 4:
        await callback.answer("Ошибка данных кнопки.")
        return

    word_id = int(parts[1])
    prefix = parts[2]
    page = int(parts[3])

    async with async_session() as session:
        word = await get_word_by_id(session, word_id)
    
    if not word:
        await callback.answer("Слово не найдено.")
        return

    text = f"🔤 <b>Слово:</b> {word.original_text}\n📝 <b>Перевод:</b> {word.translated_text}"
    
    await callback.message.edit_text(
        text, 
        reply_markup=get_word_manage_kb(word.id, word.status, prefix, page)
    )
    await callback.answer()

# Изменение статуса (Выучил / Вернуть)
@router.callback_query(F.data.startswith("set_learned:") | F.data.startswith("set_learning:"))
async def change_status(callback: types.CallbackQuery):
    # data: set_learned:ID
    parts = callback.data.split(":")
    new_status = parts[0].replace("set_", "")
    word_id = int(parts[1])
    
    async with async_session() as session:
        await update_word_status(session, word_id, new_status)
        await session.commit()
    
    status_msg = "✅ Перенесено в 'Выученные'" if new_status == "learned" else "📖 Возвращено в 'Словарь'"
    await callback.message.edit_text(status_msg)
    await callback.answer()

# Удаление слова
@router.callback_query(F.data.startswith("delete_word:"))
async def handle_delete(callback: types.CallbackQuery):
    word_id = int(callback.data.split(":")[1])
    
    async with async_session() as session:
        await delete_word(session, word_id)
        await session.commit()
    
    await callback.message.edit_text("🗑 Слово удалено из вашего словаря.")
    await callback.answer()

# Обработка ввода слова (Универсальный перехватчик - вне тренировки)
@router.message(
    F.text & ~F.text.startswith("/") & 
    ~F.text.in_([
        "🎓 Тренировка", "📖 Мой словарь", "📚 Выученные", "➕ Добавить слово", "⬅️ Назад в меню",
        "📊 Выученные за сегодняшний день", "📊 Выученные за эту неделю", "📊 Выученные за все время"
    ]),
    StateFilter(None, AddWord.waiting_for_word)
)
async def process_word_input(message: types.Message, state: FSMContext):
    # Если мы не в состоянии ожидания, но сообщение пришло - считаем это за ввод нового слова
    res = await translate_text(message.text)
    
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
