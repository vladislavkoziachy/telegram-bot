import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from src.config import BOT_TOKEN
from src.handlers import common

async def main():
    # Логирование — полезная штука, чтобы видеть в консоли, что происходит с ботом
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    # Инициализация бота и диспетчера (мозга бота)
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Регистрация наших обработчиков
    dp.include_router(common.router)

    # Запуск бота. Polling означает "опрос" новых сообщений.
    print("Бот запущен и готов к работе...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Запускаем асинхронную функцию main
    asyncio.run(main())
