from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from src.database.instance import async_session
from src.database.actions import get_or_create_user, get_words_count, get_user_words
from src.keyboards.reply import get_main_menu, get_learned_menu
from src.keyboards.inline import get_paginated_words_kb
from src.states import AddWord

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    async with async_session() as session:
        # Регистрируем пользователя
        await get_or_create_user(session, message.from_user.id)
    
    await message.answer(
        "Привет! Я твой личный помощник для изучения английского. \n"
        "Пиши любое слово — и я добавлю его в твой словарь!",
        reply_markup=get_main_menu()
    )

@router.message(F.text == "➕ Добавить слово")
async def start_add_word(message: types.Message, state: FSMContext):
    await state.set_state(AddWord.waiting_for_word)
    await message.answer("Введите слово на английском или русском языке:")

@router.message(F.text == "📚 Выученные")
async def show_learned_menu(message: types.Message):
    async with async_session() as session:
        uid = message.from_user.id
        counts = {
            "today": await get_words_count(session, uid, "learned", days=1),
            "week": await get_words_count(session, uid, "learned", days=7),
            "all": await get_words_count(session, uid, "learned")
        }
    
    await message.answer("📊 <b>Ваша статистика выученных слов:</b>", reply_markup=get_learned_menu(counts))

# Обработка выбора периода (теперь через общую функцию)
@router.message(F.text.contains("за сегодняшний день"))
async def show_today_learned(message: types.Message):
    await send_learned_page(message, 1, "today")

@router.message(F.text.contains("за эту неделю"))
async def show_week_learned(message: types.Message):
    await send_learned_page(message, 1, "week")

@router.message(F.text.contains("за все время"))
async def show_all_learned(message: types.Message):
    await send_learned_page(message, 1, "all")

# Пагинация
@router.callback_query(F.data.startswith("page:"))
async def handle_pagination(callback: types.CallbackQuery):
    # Формат: page:1:learned:today
    parts = callback.data.split(":")
    page = int(parts[1])
    prefix = parts[2]
    
    if prefix.startswith("learned_"):
        period = prefix.split("_")[1]
        await send_learned_page(callback.message, page, period, is_edit=True)
    elif prefix == "dict":
        # Передадим управление в другой хендлер или обработаем здесь
        from src.handlers.dictionary import send_dict_page
        await send_dict_page(callback.message, page, is_edit=True)
    
    await callback.answer()

async def send_learned_page(message: types.Message, page: int, period: str, is_edit: bool = False):
    days = {"today": 1, "week": 7, "all": None}[period]
    user_id = message.chat.id
    
    async with async_session() as session:
        words = await get_user_words(session, user_id, "learned", days=days)
    
    if not words:
        await message.answer("В этой категории пока пусто.")
        return

    total_pages = (len(words) - 1) // 10 + 1
    # Используем префикс learned_today (через _) для кнопок
    kb = get_paginated_words_kb(words, page, total_pages, f"learned_{period}")
    
    text = f"📖 <b>Список выученных слов</b>\nПериод: {period}\nСтраница: {page} из {total_pages}"
    
    if is_edit:
        await message.edit_text(text, reply_markup=kb)
    else:
        await message.answer(text, reply_markup=kb)

@router.message(F.text == "⬅️ Назад в меню")
async def back_to_main(message: types.Message):
    await message.answer("Главное меню:", reply_markup=get_main_menu())
