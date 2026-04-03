import asyncio
import logging
import sys
import os
from aiohttp import web

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from src.config import BOT_TOKEN, PORT
from src.handlers import common, dictionary, training
from src.database.instance import init_db

# Ссылка из настроек Render (например, https://bot.onrender.com)
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

async def on_startup(bot: Bot) -> None:
    # Инициализация базы
    await init_db()
    # Установка вебхука
    print(f"Установка вебхука на: {WEBHOOK_URL}")
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)

def main() -> None:
    # Настройка логирования
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Регистрируем роутеры
    dp.include_router(common.router)
    dp.include_router(training.router) # ТРЕНИРОВКА ТЕПЕРЬ ПРИОРИТЕТНЕЕ
    dp.include_router(dictionary.router)

    # При событии запуска (startup) вызываем нашу функцию
    dp.startup.register(on_startup)

    # Создаем aiohttp приложение
    app = web.Application()

    # Настраиваем обработчик вебхуков
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    # Регистрируем путь из WEBHOOK_URL (все что после домена)
    # Если в URL есть путь (например, /webhook), мы его вырежем
    webhook_path = "/" + WEBHOOK_URL.split("/")[-1] if "/" in WEBHOOK_URL else "/"
    webhook_requests_handler.register(app, path=webhook_path)

    # Настраиваем приложение
    setup_application(app, dp, bot=bot)

    # Запускаем сервер
    print(f"Запуск сервера на порту {PORT}...")
    web.run_app(app, host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    main()
