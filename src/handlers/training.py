import random
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from src.database import get_words
from src.keyboards.reply import get_training_menu, get_mode_menu, get_quiz_keyboard, get_main_menu, get_source_menu
from src.states import TrainingStates

router = Router()

@router.message(F.text == "🎯 Тренировка")
async def btn_training(message: Message, state: FSMContext):
    await message.answer("Выбери тренировку:", reply_markup=get_training_menu())

@router.message(F.text == "🧩 Выбери перевод")
async def btn_choose_translation(message: Message, state: FSMContext):
    await state.set_state(TrainingStates.waiting_for_source)
    await message.answer("Из какого словаря будем учить?", reply_markup=get_source_menu())

@router.message(TrainingStates.waiting_for_source, F.text)
async def process_source_selection(message: Message, state: FSMContext):
    text = message.text
    if text == "⬅️ Назад":
        await state.clear()
        await message.answer("Главное меню 👇", reply_markup=get_main_menu())
        return

    source = "learning"
    if text == "📚 Выученные":
        source = "learned"
    elif text != "📖 Мой словарь":
        await message.answer("Пожалуйста, выбери словарь кнопкой!")
        return
        
    await state.update_data(source=source)
    await state.set_state(TrainingStates.waiting_for_direction)
    await message.answer("В каком режиме будем тренироваться?", reply_markup=get_mode_menu())

@router.message(TrainingStates.waiting_for_direction, F.text)
async def process_direction_selection(message: Message, state: FSMContext):
    text = message.text
    if text == "⬅️ Назад":
        await state.clear()
        await message.answer("Главное меню 👇", reply_markup=get_main_menu())
        return

    normalized = None
    if text == "EN → RU":
        normalized = "learn_native"
    elif text == "RU → EN":
        normalized = "native_learn"
    elif text == "MIX":
        normalized = "mix"
    else:
        await message.answer("Пожалуйста, выбери режим кнопкой!", reply_markup=get_mode_menu())
        return
        
    await state.update_data(mode=normalized)
    await state.set_state(TrainingStates.waiting_for_answer)
    await send_quiz(message, state)

async def send_quiz(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    mode = data.get("mode")
    source = data.get("source", "learning")
    
    words = await get_words(user_id, "en", status=source)
    
    if len(words) < 4:
        await message.answer("Для тренировки нужно минимум 4 слова в выбранном словаре! 😢", reply_markup=get_main_menu())
        await state.clear()
        return

    correct_word = random.choice(words)
    
    current_mode = mode
    if mode == "mix":
        current_mode = random.choice(["learn_native", "native_learn"])
        
    if current_mode == "learn_native":
        question = correct_word.word
        correct_answer = correct_word.translation
        options_pool = [w.translation for w in words if w.id != correct_word.id]
    else:
        question = correct_word.translation
        correct_answer = correct_word.word
        options_pool = [w.word for w in words if w.id != correct_word.id]
        
    try:
        wrong_options = random.sample(options_pool, 3)
    except ValueError:
        wrong_options = list(set(options_pool))[:3]
        while len(wrong_options) < 3:
            wrong_options.append(correct_answer + "_")
        
    options = [correct_answer] + wrong_options[:3]
    random.shuffle(options)
    
    await state.update_data(correct_answer=correct_answer)
    await message.answer(f"👉 {question}", reply_markup=get_quiz_keyboard(options))

@router.message(TrainingStates.waiting_for_answer, F.text)
async def process_quiz_answer(message: Message, state: FSMContext):
    text = message.text
    if text == "⬅️ Назад":
        await state.clear()
        await message.answer("Главное меню 👇", reply_markup=get_main_menu())
        return

    data = await state.get_data()
    correct_answer = data.get("correct_answer")
    
    if text == correct_answer:
        await message.answer("🔥 Правильно!")
    else:
        await message.answer(f"❌ Неправильно\nПравильный ответ: {correct_answer}")
        
    await send_quiz(message, state)
