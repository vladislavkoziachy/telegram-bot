import random
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from src.database.instance import async_session
from src.database.actions import get_user_words, get_word_by_id, update_word_status
from src.keyboards.inline import get_quiz_kb
from src.keyboards.reply import get_main_menu
from src.services.voice import send_voice_pronunciation
from src.states import Training

router = Router()

@router.message(F.text == "🎓 Тренировка")
async def start_training(message: types.Message, state: FSMContext):
    async with async_session() as session:
        # Берем слова, которые пользователь СЕЙЧАС учит
        words = await get_user_words(session, message.from_user.id, "learning")
    
    if len(words) < 1:
        await message.answer("📖 В вашем словаре пока нет слов для тренировки. \nСначала добавьте хотя бы одно слово!")
        return

    # Выбираем случайное слово для вопроса
    word = random.choice(words)
    
    # Формируем варианты ответов (упрощенно: правильный + 3 случайных из общего списка)
    # В идеале нужно брать случайные слова из базы, но для MVP возьмем заглушки, если слов мало
    options = [{"text": word.translated_text, "is_correct": "yes"}]
    
    # Добавим 3 неправильных варианта (в будущем можно брать из базы)
    decoys = ["Apple", "Book", "House", "Car", "Sun", "Water", "Friend"]
    random.shuffle(decoys)
    for i in range(3):
        options.append({"text": decoys[i], "is_correct": "no"})
    
    random.shuffle(options)

    # Отправляем вопрос
    await message.answer(
        f"Как переводится слово: <b>{word.original_text}</b>?",
        reply_markup=get_quiz_kb(options, word.id)
    )
    
    # Озвучиваем (если это английское слово)
    from src.services.translator import is_russian
    if not is_russian(word.original_text):
        await send_voice_pronunciation(message, word.original_text)

# Обработка ответа в квизе
@router.callback_query(F.data.startswith("quiz_"))
async def handle_quiz_answer(callback: types.CallbackQuery):
    # data: quiz_yes_ID или quiz_no_ID
    parts = callback.data.split("_")
    is_correct = parts[1] == "yes"
    word_id = int(parts[2])
    
    async with async_session() as session:
        word = await get_word_by_id(session, word_id)

    if is_correct:
        await callback.message.edit_text(
            f"✅ <b>Верно!</b>\n{word.original_text} — это {word.translated_text}."
        )
        # В будущем здесь можно добавить логику переноса в 'Выученные' после 3-5 успехов
    else:
        await callback.message.edit_text(
            f"❌ <b>Ошибка.</b>\nПравильный ответ: <b>{word.translated_text}</b>"
        )
    
    await callback.answer()
    # Сразу предлагаем следующую тренировку? Или возвращаемся в меню.
    await callback.message.answer("Выберите действие:", reply_markup=get_main_menu())
