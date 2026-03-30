from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from typing import Callable

from src.database import add_word, get_words, update_word_status, delete_word
from src.keyboards.inline import get_dictionary_keyboard, get_word_action_keyboard, get_add_word_keyboard
from src.keyboards.reply import get_main_menu
from src.states import AddingWordStates
from src.services.translator import translate_word, FLAGS
from src.services.tts import generate_audio
from aiogram.types import FSInputFile
import os

router = Router()

@router.message(F.text.in_(["➕ Добавить слово", "➕ Додати слово", "➕ Dodaj słowo"]))
async def btn_add_word(message: Message, state: FSMContext, _: Callable):
    from src.keyboards.reply import get_back_button
    await state.set_state(AddingWordStates.waiting_for_word)
    await message.answer(_("welcome_word_add", default="Напиши слово на английском или русском ✍️"), reply_markup=get_back_button(_))

@router.message(AddingWordStates.waiting_for_word, F.text)
async def process_word_to_add(message: Message, state: FSMContext, _: Callable, user_lang: str, learn_lang: str):
    text = message.text
    if text in ["⬅️ Назад", "⬅️ Взад", "⬅️ Wstecz"]:
        await state.clear()
        await message.answer(_("main_menu_text"), reply_markup=get_main_menu(_))
        return

    word_learn, word_native = translate_word(text, user_lang=user_lang, learn_lang=learn_lang)
    keyboard = get_add_word_keyboard(_, word_learn, word_native)
    flag_learn = FLAGS.get(learn_lang, "")
    flag_native = FLAGS.get(user_lang, "")
    await message.answer(f"{flag_learn} {word_learn} \n{flag_native} {word_native}", reply_markup=keyboard)
    
@router.callback_query(F.data.startswith("add:"))
async def cb_add_word(callback: CallbackQuery, state: FSMContext, learn_lang: str):
    parts = callback.data.split(":")
    word_learn = parts[1]
    word_native = parts[2]
    user_id = callback.from_user.id
    
    added = await add_word(user_id, word_learn, word_native, learn_lang)
    if not added:
        await callback.answer("⚠️", show_alert=True)
        return
        
    await callback.message.edit_text(f"✅ {word_learn} — {word_native}")
    await state.clear()

async def show_dictionary_page(message_or_cb, user_id: int, learn_lang: str, status: str, page: int, prefix: str, title: str, _: Callable, since=None, per_page: int=20):
    words = await get_words(user_id, learn_lang, status, since=since)
    if not words:
        msg = "Empty 😢"
        if isinstance(message_or_cb, Message):
            await message_or_cb.answer(msg)
        else:
            await message_or_cb.answer(msg, show_alert=True)
        return
        
    keyboard = get_dictionary_keyboard(_, words, page=page, prefix=prefix, per_page=per_page)
    
    text = f"{title} ({len(words)})"
    if len(words) > per_page:
        text += f"\nPage {page+1}:"
    
    if isinstance(message_or_cb, Message):
        await message_or_cb.answer(text, reply_markup=keyboard)
    else:
        await message_or_cb.message.edit_text(text, reply_markup=keyboard)

@router.message(F.text.in_(["📖 Мой словарь", "📖 Мій словник", "📖 Mój słownik"]))
async def btn_dictionary(message: Message, _: Callable, learn_lang: str):
    await show_dictionary_page(message, message.from_user.id, learn_lang, 'learning', 0, "dic", _("menu_my_dictionary"), _, per_page=10)

@router.callback_query(F.data.startswith("dic_page:"))
async def cb_dic_page(callback: CallbackQuery, _: Callable, learn_lang: str):
    page = int(callback.data.split(":")[1])
    await show_dictionary_page(callback, callback.from_user.id, learn_lang, 'learning', page, "dic", _("menu_my_dictionary"), _, per_page=10)

@router.message(F.text.in_(["📚 Выученные", "📚 Вивчені", "📚 Wyuczone"]))
async def btn_learned_menu_trigger(message: Message, _: Callable, learn_lang: str):
    from src.database import count_words
    from datetime import datetime, timedelta
    from src.keyboards.reply import get_learned_menu
    
    user_id = message.from_user.id
    total = await count_words(user_id, learn_lang, 'learned')
    week = await count_words(user_id, learn_lang, 'learned', datetime.utcnow() - timedelta(days=7))
    today = await count_words(user_id, learn_lang, 'learned', datetime.utcnow().replace(hour=0, minute=0, second=0))
    
    await message.answer(_("menu_learned"), reply_markup=get_learned_menu(_, total, week, today))

@router.message(F.text.startswith("Показать все выученные слова"))
@router.message(F.text.startswith("Показати всі вивчені слова"))
@router.message(F.text.startswith("Pokaż wszystkie wyuczone słowa"))
async def btn_show_all_learned(message: Message, _: Callable, learn_lang: str):
    await show_dictionary_page(message, message.from_user.id, learn_lang, 'learned', 0, "learn", _("menu_learned"), _, per_page=20)

@router.callback_query(F.data.startswith("word:"))
async def cb_word_action(callback: CallbackQuery, _: Callable, learn_lang: str):
    parts = callback.data.split(":")
    prefix = parts[1]
    word = parts[2]
    
    from src.database import get_words
    from src.keyboards.inline import get_word_action_keyboard, get_learned_word_action_keyboard
    
    user_id = callback.from_user.id
    words_learning = await get_words(user_id, learn_lang, "learning")
    words_learned = await get_words(user_id, learn_lang, "learned")
    all_words = words_learning + words_learned
    
    translation = ""
    full_word = word
    for w in all_words:
        if w.word.startswith(word):
            translation = w.translation
            full_word = w.word
            break
            
    if prefix.startswith("learn"):
        keyboard = get_learned_word_action_keyboard(_, full_word, prefix)
    else:
        keyboard = get_word_action_keyboard(_, full_word, prefix)
        
    await callback.message.edit_text(f"{full_word} — {translation}", reply_markup=keyboard)

@router.callback_query(F.data.startswith("voice:"))
async def cb_pronounce_word(callback: CallbackQuery, learn_lang: str):
    word = callback.data.split(":")[1]
    await callback.answer("⏳...")
    filename = f"{word}.mp3"
    
    try:
        await generate_audio(word, filename, lang=learn_lang)
        voice_file = FSInputFile(filename)
        await callback.message.answer_voice(voice=voice_file)
    except Exception:
        await callback.message.answer("❌ Error.")
    finally:
        if os.path.exists(filename):
            os.remove(filename)

@router.callback_query(F.data == "ignore")
async def cb_ignore(callback: CallbackQuery):
    await callback.answer()

async def return_to_list(callback: CallbackQuery, user_id: int, learn_lang: str, prefix: str, _: Callable):
    if prefix == "dic":
        await show_dictionary_page(callback, user_id, learn_lang, 'learning', 0, "dic", _("menu_my_dictionary"), _, per_page=10)
    elif prefix == "learn":
        await show_dictionary_page(callback, user_id, learn_lang, 'learned', 0, "learn", _("menu_learned"), _, per_page=20)

@router.callback_query(F.data.startswith("learn:"))
async def cb_learn_word(callback: CallbackQuery, _: Callable, learn_lang: str):
    parts = callback.data.split(":")
    prefix = parts[1]
    word = parts[2]
    await update_word_status(callback.from_user.id, learn_lang, word, "learned")
    await callback.answer(f"✅ {word}", show_alert=True)
    await return_to_list(callback, callback.from_user.id, learn_lang, prefix, _)

@router.callback_query(F.data.startswith("unlearn:"))
async def cb_unlearn_word(callback: CallbackQuery, _: Callable, learn_lang: str):
    parts = callback.data.split(":")
    prefix = parts[1]
    word = parts[2]
    await update_word_status(callback.from_user.id, learn_lang, word, "learning")
    await callback.answer(f"↩️ {word}", show_alert=True)
    await return_to_list(callback, callback.from_user.id, learn_lang, prefix, _)

@router.callback_query(F.data.startswith("delete:"))
async def cb_delete_word(callback: CallbackQuery, _: Callable, learn_lang: str):
    parts = callback.data.split(":")
    prefix = parts[1]
    word = parts[2]
    await delete_word(callback.from_user.id, learn_lang, word)
    await callback.answer(f"❌ {word}", show_alert=True)
    await return_to_list(callback, callback.from_user.id, learn_lang, prefix, _)

@router.callback_query(F.data.startswith("back_list:"))
async def cb_back_list(callback: CallbackQuery, _: Callable, learn_lang: str):
    prefix = callback.data.split(":")[1]
    await return_to_list(callback, callback.from_user.id, learn_lang, prefix, _)
