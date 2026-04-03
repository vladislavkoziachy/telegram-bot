import random
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from src.database.instance import async_session
from src.database.actions import get_user_words, get_word_by_id
from src.keyboards.inline import (
    get_quiz_kb, 
    get_training_type_kb, 
    get_training_pool_kb, 
    get_training_direction_kb
)
from src.keyboards.reply import get_main_menu
from src.services.voice import send_voice_pronunciation
from src.services.translator import is_russian
from src.states import Training

router = Router()

# Стартовое меню настройки тренировки
@router.message(F.text == "🎓 Тренировка")
async def start_training_config(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(Training.choosing_type)
    await message.answer(
        "🎯 <b>Выберите тренировку:</b>",
        reply_markup=get_training_type_kb()
    )

# 1. Обработка выбора типа
@router.callback_query(F.data == "train_type_choice", Training.choosing_type)
async def handle_type_choice(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Training.choosing_pool)
    await callback.message.edit_text(
        "📂 <b>Какие слова будем тренировать?</b>",
        reply_markup=get_training_pool_kb()
    )
    await callback.answer()

# 2. Обработка выбора папки
@router.callback_query(F.data.startswith("train_pool_"), Training.choosing_pool)
async def handle_pool_choice(callback: types.CallbackQuery, state: FSMContext):
    pool = callback.data.replace("train_pool_", "")
    await state.update_data(pool=pool)
    
    await state.set_state(Training.choosing_direction)
    await callback.message.edit_text(
        "🔄 <b>Выбери режим перевода (RU EN / EN RU / MIX):</b>",
        reply_markup=get_training_direction_kb()
    )
    await callback.answer()

# 3. Обработка направления и ЗАПУСК квиза
@router.callback_query(F.data.startswith("train_dir_"), Training.choosing_direction)
async def handle_direction_choice(callback: types.CallbackQuery, state: FSMContext):
    direction = callback.data.replace("train_dir_", "")
    await state.update_data(direction=direction)
    
    await callback.answer("Начинаем!")
    await send_next_question(callback.message, state)

# Функция генерации и отправки вопроса
async def send_next_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    pool = data.get('pool', 'learning')
    direction = data.get('direction', 'mix')
    
    async with async_session() as session:
        words = await get_user_words(session, message.chat.id, pool)
    
    if len(words) < 1:
        status_text = "словарном запасе" if pool == "learning" else "списке выученных"
        await message.answer(f"🤔 В вашем {status_text} пока нет слов. Добавьте слова, чтобы начать!")
        await state.clear()
        return

    # Выбираем случайное слово
    word = random.choice(words)
    
    # Определяем направление для ЭТОГО вопроса
    current_dir = direction
    if direction == "mix":
        current_dir = random.choice(["ru_en", "en_ru"])
    
    if current_dir == "en_ru":
        if is_russian(word.original_text):
             question_text, correct_answer = word.translated_text, word.original_text
        else:
             question_text, correct_answer = word.original_text, word.translated_text
    else:
        if is_russian(word.original_text):
            question_text, correct_answer = word.original_text, word.translated_text
        else:
            question_text, correct_answer = word.translated_text, word.original_text

    # Генерируем варианты
    options = [{"text": correct_answer, "is_correct": "yes"}]
    decoys = ["Apple", "Book", "House", "Car", "Sun", "Water", "Friend", "Sky", "Table"]
    random.shuffle(decoys)
    for i in range(3):
        options.append({"text": decoys[i], "is_correct": "no"})
    
    random.shuffle(options)

    # Сохраняем правильный ответ в состояние
    await state.update_data(correct_answer=correct_answer)

    # Отправляем сообщение
    msg = await message.answer(
        f"Как переводится: <b>{question_text}</b>?",
        reply_markup=get_quiz_kb(options, word.id)
    )
    
    if not is_russian(question_text):
        await send_voice_pronunciation(msg, question_text)

# Остановка тренировки
@router.callback_query(F.data == "train_stop")
async def stop_training(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer("Тренировка остановлена. Возвращаемся в меню!", reply_markup=get_main_menu())
    await callback.answer()

# Обработка ответа
@router.callback_query(F.data.startswith("quiz_"))
async def handle_quiz_answer(callback: types.CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    is_correct = parts[1] == "yes"
    word_id = int(parts[2])
    
    async with async_session() as session:
        word = await get_word_by_id(session, word_id)
    
    if not word:
        await callback.answer("Ошибка: слово исчезло.")
        return

    # Показываем результат (верно/неверно) коротким алертом
    feedback = "✅ Круто! Верно." if is_correct else f"❌ Ошибка. Правильно: {word.translated_text}"
    await callback.answer(feedback, show_alert=False)

    # УДАЛЯЕМ старый вопрос, чтобы чат не превращался в свалку (опционально)
    # но пользователь просил "слова за словом", так что просто присылаем новое
    await send_next_question(callback.message, state)
