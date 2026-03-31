from aiogram import Router, types
from aiogram.filters import Command
from src.keyboards.reply import get_main_menu

# Router помогает нам разделять логику на разные файлы
router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я твой личный помощник для изучения английского. \n"
        "Давай начнем учить новые слова! 🚀",
        reply_markup=get_main_menu()
    )
