import random
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from typing import Callable

from src.database import get_words
from src.keyboards.reply import get_training_menu, get_mode_menu, get_quiz_keyboard, get_main_menu
from src.states import TrainingStates
from src.services.i18n import get_all_translated

router = Router()

@router.message(F.text.in_(get_all_translated("menu_training")))
async def btn_training(message: Message, state: FSMContext, _: Callable):
    from src.keyboards.reply import get_source_menu
    await state.set_state(TrainingStates.waiting_for_source)
    await message.answer(_("choose_dictionary", default="Из какого словаря будем учить?"), reply_markup=get_source_menu(_))

@router.message(TrainingStates.waiting_for_source, F.text)
async def process_source_selection(message: Message, state: FSMContext, _: Callable):
    text = message.text
    if text in get_all_translated("btn_back") + ["⬅️ Назад", "⬅️ Взад", "⬅️ Wstecz"]:
        await state.clear()
        await message.answer(_("main_menu_text"), reply_markup=get_main_menu(_))
        return

    source = "learning"
    if text in get_all_translated("menu_learned"):
        source = "learned"
    elif text not in get_all_translated("menu_my_dictionary"):
        await message.answer(_("choose_dictionary", default="Из какого словаря будем учить?"))
        return
        
    await state.update_data(source=source)
    await state.set_state(TrainingStates.waiting_for_direction)
    
    from src.keyboards.reply import get_mode_menu
    await message.answer(_("choose_mode", default="В каком режиме будем тренироваться?"), reply_markup=get_mode_menu(_))

@router.message(TrainingStates.waiting_for_direction, F.text)
async def process_direction_selection(message: Message, state: FSMContext, _: Callable):
    text = message.text
    if text in get_all_translated("btn_back") + ["⬅️ Назад", "⬅️ Взад", "⬅️ Wstecz"]:
        await state.clear()
        await message.answer(_("main_menu_text"), reply_markup=get_main_menu(_))
        return

    if text in get_all_translated("training_learn_native"):
        normalized = "learn_native"
    elif text in get_all_translated("training_native_learn"):
        normalized = "native_learn"
    elif text in get_all_translated("training_mix"):
        normalized = "mix"
    else:
        from src.keyboards.reply import get_mode_menu
        await message.answer(_("choose_mode", default="В каком режиме будем тренироваться?"), reply_markup=get_mode_menu(_))
        return
        
    await state.update_data(mode=normalized)
    await state.set_state(TrainingStates.waiting_for_answer)
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
    
    keyboard = get_quiz_keyboard(options, stop_text=_("btn_back")) # Using btn_back as stop
    await message.answer(f"👉 {question}", reply_markup=keyboard)

@router.message(TrainingStates.waiting_for_answer, F.text)
async def process_quiz_answer(message: Message, state: FSMContext, _: Callable, learn_lang: str):
    text = message.text
    if text in get_all_translated("btn_back") + ["🛑 Окончить тренировку", "🛑 Завершить тренировку"]:
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
