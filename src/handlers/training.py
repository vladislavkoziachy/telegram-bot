import random
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from typing import Callable

from src.database import get_words
from src.keyboards.reply import get_training_menu, get_mode_menu, get_quiz_keyboard, get_main_menu
from src.states import TrainingStates

router = Router()

@router.message(F.text.in_(["🎯 Тренировка", "🎯 Тренування", "🎯 Trening"]))
async def btn_training(message: Message, _: Callable):
    await message.answer(_("menu_training"), reply_markup=get_training_menu(_))

@router.message(F.text == "🎯 Выбери перевод") # TODO: i18n
async def btn_choose_translation(message: Message, _: Callable):
    from src.keyboards.reply import get_source_menu
    await message.answer(_("welcome_learning"), reply_markup=get_source_menu(_))

@router.message(F.text.in_(["📖 Учить новые слова", "📖 Мій словник", "📖 Mój słownik", "📚 Выученные", "📚 Вивчені", "📚 Wyuczone"]))
async def btn_choose_source(message: Message, state: FSMContext, _: Callable):
    # Mapping back to internal status
    text = message.text
    source = "learning"
    if text in ["📚 Выученные", "📚 Вивчені", "📚 Wyuczone"]:
        source = "learned"
        
    await state.update_data(source=source)
    await message.answer(_("welcome_learning"), reply_markup=get_mode_menu(_))

@router.message(F.text.in_(["EN → RU", "RU → EN", "MIX"]))
async def start_quiz_mode(message: Message, state: FSMContext, _: Callable):
    await state.set_state(TrainingStates.waiting_for_answer)
    await state.update_data(mode=message.text)
    await send_quiz(message, state, _)

async def send_quiz(message: Message, state: FSMContext, _: Callable):
    user_id = message.from_user.id
    data = await state.get_data()
    mode = data.get("mode")
    source = data.get("source", "learning")
    learn_lang = data.get("learn_lang", "en") # Should be in data from middleware or needs to be passed
    
    # We can get learn_lang from state data or from the database directly, 
    # but middleware already injected it into the handler's kwargs.
    # To use it in send_quiz, we should pass it or fetch from state.
    
    from src.database import get_words
    words = await get_words(user_id, learn_lang, status=source)
    
    if len(words) < 4:
        await message.answer("❌ < 4 words", reply_markup=get_main_menu(_))
        await state.clear()
        return

    correct_word = random.choice(words)
    
    current_mode = mode
    if mode == "MIX":
        current_mode = random.choice(["EN → RU", "RU → EN"])
        
    if current_mode == "EN → RU":
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
    
    keyboard = get_quiz_keyboard(options, stop_text=_("btn_back")) # Using btn_back as stop
    await message.answer(f"👉 {question}", reply_markup=keyboard)

@router.message(TrainingStates.waiting_for_answer, F.text)
async def process_quiz_answer(message: Message, state: FSMContext, _: Callable, learn_lang: str):
    text = message.text
    if text in ["🛑 Окончить тренировку", "🛑 Завершить тренировку", "⬅️ Назад", "⬅️ Назад", "⬅️ Взад", "⬅️ Wstecz"]:
        await state.clear()
        await message.answer(_("main_menu_text"), reply_markup=get_main_menu(_))
        return

    data = await state.get_data()
    correct_answer = data.get("correct_answer")
    
    if text == correct_answer:
        await message.answer("🔥")
    else:
        await message.answer(f"❌ -> {correct_answer}")
        
    # We need to pass learn_lang into send_quiz's state data for it to work
    await state.update_data(learn_lang=learn_lang)
    await send_quiz(message, state, _)
