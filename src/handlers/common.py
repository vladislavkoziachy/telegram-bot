from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from src.database.instance import async_session
from src.database.actions import get_or_create_user, get_words_count, get_user_words
from src.keyboards.reply import get_main_menu, get_learned_menu
from src.keyboards.inline import get_words_list_kb
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
        # Считаем слова для счетчиков
        uid = message.from_user.id
        counts = {
            "today": await get_words_count(session, uid, "learned", days=1),
            "week": await get_words_count(session, uid, "learned", days=7),
            "all": await get_words_count(session, uid, "learned")
        }
    
    await message.answer("Раздел выученных слов:", reply_markup=get_learned_menu(counts))

@router.message(F.text.startswith("📅 Выучено за сегодня"))
async def show_learned_today(message: types.Message):
    async with async_session() as session:
        words = await get_user_words(session, message.from_user.id, "learned", days=1)
    
    if not words:
        await message.answer("В этой категории пока пусто.")
        return
    
    await message.answer("Слова, закрепленные сегодня:", reply_markup=get_words_list_kb(words))

@router.message(F.text.startswith("📅 Выучено за неделю"))
async def show_learned_week(message: types.Message):
    async with async_session() as session:
        words = await get_user_words(session, message.from_user.id, "learned", days=7)
    
    if not words:
        await message.answer("В этой категории пока пусто.")
        return
    
    await message.answer("Слова, закрепленные за неделю:", reply_markup=get_words_list_kb(words))

@router.message(F.text.startswith("📅 Выучено за всё время"))
async def show_learned_all(message: types.Message):
    async with async_session() as session:
        words = await get_user_words(session, message.from_user.id, "learned")
    
    if not words:
        await message.answer("В этой категории пока пусто.")
        return
    
    await message.answer("Ваш список триумфа!", reply_markup=get_words_list_kb(words))

@router.message(F.text == "⬅️ Назад в меню")
async def back_to_main(message: types.Message):
    await message.answer("Главное меню:", reply_markup=get_main_menu())
