import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///words.db")

if not BOT_TOKEN:
    exit("Ошибка: BOT_TOKEN не найден в .env")
