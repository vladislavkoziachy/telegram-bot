from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from src.states import AddWord

router = Router()

# 1. Начало процесса: бот получил слово
@router.message(AddWord.waiting_for_word)
async def process_word(message: types.Message, state: FSMContext):
    # Сохраняем введенное слово во временное хранилище (State)
    await state.update_data(word=message.text)
    
    # Переходим к следующему шагу
    await state.set_state(AddWord.waiting_for_translation)
    await message.answer(f"Отлично! Слово '<b>{message.text}</b>' принято. \nТеперь введите его перевод:")

# 2. Финал процесса: бот получил перевод
@router.message(AddWord.waiting_for_translation)
async def process_translation(message: types.Message, state: FSMContext):
    # Достаем из памяти слово, которое ввели ранее
    user_data = await state.get_data()
    word = user_data.get("word")
    translation = message.text
    
    # Пока базы нет, просто подтверждаем успех
    await message.answer(
        f"✅ Готово! \n"
        f"<b>Слово:</b> {word} \n"
        f"<b>Перевод:</b> {translation} \n\n"
        f"<i>(На следующем шаге я научусь сохранять это в базу данных!)</i>"
    )
    
    # Очищаем состояние (бот больше не ждет ввода)
    await state.clear()
