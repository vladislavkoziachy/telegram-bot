import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from src.config import BOT_TOKEN, PORT
from src.handlers import common, dictionary
from src.services.keep_alive import start_keep_alive

async def main():
    # Логирование — полезная штука, чтобы видеть в консоли, что происходит с ботом
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    # Инициализация бота и диспетчера (мозга бота)
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Запускаем фиктивный сервер для Render
    await start_keep_alive()

    # Регистрация наших обработчиков
    dp.include_router(common.router)
    dp.include_router(dictionary.router)

    # Удаляем вебхук, если он был установлен ранее, чтобы избежать конфликтов
    print("Очистка вебхуков...")
    await bot.delete_webhook(drop_pending_updates=True)
    await asyncio.sleep(2) # Небольшая пауза для сброса соединений Telegram

    # Запуск бота. Polling означает "опрос" новых сообщений.
    print("Бот запущен и готов к работе...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Запускаем асинхронную функцию main
    asyncio.run(main())
