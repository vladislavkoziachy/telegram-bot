from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from src.keyboards.reply import get_main_menu
from src.keyboards.inline import get_learned_menu
from src.states import AddWord

# Router помогает нам разделять логику на разные файлы
router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    # Очищаем все старые состояния, если они были
    await state.clear()
    
    await message.answer(
        "Привет! Я твой личный помощник для изучения английского. \n"
        "Давай начнем учить новые слова! 🚀",
        reply_markup=get_main_menu()
    )

# 1. Нажатие на "➕ Добавить слово"
@router.message(F.text == "➕ Добавить слово")
async def cmd_add_word(message: types.Message, state: FSMContext):
    # Переводим бота в режим ожидания слова
    await state.set_state(AddWord.waiting_for_word)
    await message.answer("Хорошо! Введите слово на <b>английском</b>, которое хотите добавить:")

# 2. Нажатие на "📖 Мой словарь"
@router.message(F.text == "📖 Мой словарь")
async def cmd_my_dictionary(message: types.Message):
    await message.answer("📖 В вашем словаре пока нет слов. \nЧтобы добавить слово, нажмите кнопку выше! 👇")

# 3. Нажатие на "📚 Выученные"
@router.message(F.text == "📚 Выученные")
async def cmd_learned(message: types.Message):
    await message.answer(
        "📚 Здесь будут слова, которые вы уже выучили. \nВыберите категорию:",
        reply_markup=get_learned_menu()
    )
