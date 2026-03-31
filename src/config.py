import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 10000))
DATABASE_URL = os.getenv("DATABASE_URL") or "sqlite+aiosqlite:///words.db"

if not BOT_TOKEN:
    exit("Ошибка: BOT_TOKEN не найден в .env")
