import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from src.database import add_word, get_words, update_word_status, delete_word
from src.keyboards.inline import get_dictionary_keyboard, get_word_action_keyboard, get_add_word_keyboard
from src.keyboards.reply import get_main_menu, get_back_button, get_learned_menu
from src.states import AddingWordStates
from src.services.translator import translate_word
from src.services.tts import generate_audio
from aiogram.types import FSInputFile
import os

router = Router()
logger = logging.getLogger(__name__)

MAIN_MENU_BUTTONS = ["➕ Добавить слово", "📖 Мой словарь", "🎯 Тренировка", "📚 Выученные", "🌐 Переводчик", "⚙️ Настройки"]

@router.message(F.text == "➕ Добавить слово")
async def btn_add_word(message: Message, state: FSMContext):
    await state.set_state(AddingWordStates.waiting_for_word)
    await message.answer("Напиши слово на английском или русском ✍️", reply_markup=get_back_button())

@router.message(AddingWordStates.waiting_for_word, F.text)
async def process_word_to_add(message: Message, state: FSMContext):
    text = message.text
    logger.info(f"User {message.from_user.id} in AddingWordStates: {text}")
    
    if text == "⬅️ Назад":
        await state.clear()
        await message.answer("Главное меню 👇", reply_markup=get_main_menu())
        return

    # If user clicks another menu button, clear state and don't translate
    if text in MAIN_MENU_BUTTONS:
        await state.clear()
        # We return False or just let other handlers catch it by not returning? 
        # In aiogram, we can't easily "fall through" from a state handler to a non-state handler in the same router easily if it matched.
        # But we can manually call the handler or just tell them we switched. 
        # Better: just tell them we are back in main menu and they should click again, or clear and return so common.py doesnt catch it.
        # Actually, if we clear state here, and the router continues? No, it won't.
        # Let's just state that we cancelled and show the menu.
        await message.answer("Ввод слова отменен. Переходим в другой раздел... 🔄")
        return

    word_learn, word_native = translate_word(text)
    keyboard = get_add_word_keyboard(word_learn, word_native)
    await message.answer(f"🇬🇧 {word_learn} \n🇷🇺 {word_native}", reply_markup=keyboard)
    
@router.callback_query(F.data.startswith("add:"))
async def cb_add_word(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    parts = callback.data.split(":")
    word_learn = parts[1]
    word_native = parts[2]
    user_id = callback.from_user.id
    
    # Always English for now
    added = await add_word(user_id, word_learn, word_native, "en")
    if not added:
        await callback.answer("⚠️ Это слово уже есть в словаре", show_alert=True)
        return
        
    await callback.message.edit_text(f"✅ {word_learn} — {word_native}")
    await state.clear()

async def show_dictionary_page(message_or_cb, user_id: int, status: str, page: int, prefix: str, title: str, since=None, per_page: int=20):
    words = await get_words(user_id, "en", status, since=since)
    if not words:
        msg = "В этом разделе пока пусто 😢"
        if isinstance(message_or_cb, Message):
            await message_or_cb.answer(msg)
        else:
            await message_or_cb.answer(msg, show_alert=True)
        return
        
    keyboard = get_dictionary_keyboard(words, page=page, prefix=prefix, per_page=per_page)
    
    text = f"{title} ({len(words)})"
    if len(words) > per_page:
        text += f"\nСтраница {page+1}:"
    
    if isinstance(message_or_cb, Message):
        await message_or_cb.answer(text, reply_markup=keyboard)
    else:
        await message_or_cb.message.edit_text(text, reply_markup=keyboard)

@router.message(F.text == "📖 Мой словарь")
async def btn_dictionary(message: Message):
    await show_dictionary_page(message, message.from_user.id, 'learning', 0, "dic", "📖 Мой словарь", per_page=20)

@router.callback_query(F.data.startswith("dic_page:"))
async def cb_dic_page(callback: CallbackQuery):
    await callback.answer()
    page = int(callback.data.split(":")[1])
    await show_dictionary_page(callback, callback.from_user.id, 'learning', page, "dic", "📖 Мой словарь", per_page=20)

@router.message(F.text == "📚 Выученные")
async def btn_learned_menu_trigger(message: Message):
    from src.database import count_words
    from datetime import datetime, timedelta
    
    user_id = message.from_user.id
    total = await count_words(user_id, "en", 'learned')
    week = await count_words(user_id, "en", 'learned', datetime.utcnow() - timedelta(days=7))
    today = await count_words(user_id, "en", 'learned', datetime.utcnow().replace(hour=0, minute=0, second=0))
    
    await message.answer("📚 Выученные слова:", reply_markup=get_learned_menu(total, week, today))

@router.message(F.text.func(lambda text: "все выученные слова" in text.lower()))
async def btn_show_all_learned(message: Message):
    await show_dictionary_page(message, message.from_user.id, 'learned', 0, "learn", "📚 Все выученные", per_page=20)

@router.message(F.text.func(lambda text: "за неделю" in text.lower()))
async def btn_show_week_learned(message: Message):
    from datetime import datetime, timedelta
    since = datetime.utcnow() - timedelta(days=7)
    await show_dictionary_page(message, message.from_user.id, 'learned', 0, "learn", "📅 Выученные за неделю", since=since, per_page=20)

@router.message(F.text.func(lambda text: "за сегодня" in text.lower()))
async def btn_show_today_learned(message: Message):
    from datetime import datetime
    since = datetime.utcnow().replace(hour=0, minute=0, second=0)
    await show_dictionary_page(message, message.from_user.id, 'learned', 0, "learn", "🕒 Выученные за сегодня", since=since, per_page=20)

@router.callback_query(F.data.startswith("word:"))
async def cb_word_action(callback: CallbackQuery):
    await callback.answer()
    parts = callback.data.split(":")
    prefix = parts[1]
    word = parts[2]
    
    from src.database import get_words
    from src.keyboards.inline import get_word_action_keyboard, get_learned_word_action_keyboard
    
    user_id = callback.from_user.id
    words_learning = await get_words(user_id, "en", "learning")
    words_learned = await get_words(user_id, "en", "learned")
    all_words = words_learning + words_learned
    
    translation = ""
    full_word = word
    for w in all_words:
        if w.word.startswith(word):
            translation = w.translation
            full_word = w.word
            break
            
    if prefix.startswith("learn"):
        keyboard = get_learned_word_action_keyboard(full_word, prefix)
    else:
        keyboard = get_word_action_keyboard(full_word, prefix)
        
    await callback.message.edit_text(f"{full_word} — {translation}", reply_markup=keyboard)

@router.callback_query(F.data.startswith("voice:"))
async def cb_pronounce_word(callback: CallbackQuery):
    word = callback.data.split(":")[1]
    await callback.answer("⏳...")
    filename = f"{word}.mp3"
    
    try:
        await generate_audio(word, filename)
        voice_file = FSInputFile(filename)
        await callback.message.answer_voice(voice=voice_file)
    except Exception:
        await callback.message.answer("❌ Ошибка при генерации озвучки.")
    finally:
        if os.path.exists(filename):
            os.remove(filename)

@router.callback_query(F.data == "ignore")
async def cb_ignore(callback: CallbackQuery):
    await callback.answer()

async def return_to_list(callback: CallbackQuery, user_id: int, prefix: str):
    if prefix == "dic":
        await show_dictionary_page(callback, user_id, 'learning', 0, "dic", "📖 Мой словарь", per_page=20)
    elif prefix == "learn":
        await show_dictionary_page(callback, user_id, 'learned', 0, "learn", "📚 Все выученные", per_page=20)

@router.callback_query(F.data.startswith("learn:"))
async def cb_learn_word(callback: CallbackQuery):
    parts = callback.data.split(":")
    prefix = parts[1]
    word = parts[2]
    await update_word_status(callback.from_user.id, "en", word, "learned")
    await callback.answer(f"✅ {word} перенесено в выученные!", show_alert=True)
    await return_to_list(callback, callback.from_user.id, prefix)

@router.callback_query(F.data.startswith("unlearn:"))
async def cb_unlearn_word(callback: CallbackQuery):
    parts = callback.data.split(":")
    prefix = parts[1]
    word = parts[2]
    await update_word_status(callback.from_user.id, "en", word, "learning")
    await callback.answer(f"↩️ {word} вернулось в словарь для изучения", show_alert=True)
    await return_to_list(callback, callback.from_user.id, prefix)

@router.callback_query(F.data.startswith("delete:"))
async def cb_delete_word(callback: CallbackQuery):
    parts = callback.data.split(":")
    prefix = parts[1]
    word = parts[2]
    await delete_word(callback.from_user.id, "en", word)
    await callback.answer(f"❌ {word} удалено из словаря", show_alert=True)
    await return_to_list(callback, callback.from_user.id, prefix)

@router.callback_query(F.data.startswith("back_list:"))
async def cb_back_list(callback: CallbackQuery):
    await callback.answer()
    prefix = callback.data.split(":")[1]
    await return_to_list(callback, callback.from_user.id, prefix)
