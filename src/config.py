import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 10000))
# Настройки базы данных
# Для Supabase (PostgreSQL) нам нужно добавить префикс +asyncpg, если его нет
URL = os.getenv("DATABASE_URL") or "sqlite+aiosqlite:///words.db"
if URL.startswith("postgresql://"):
    URL = URL.replace("postgresql://", "postgresql+asyncpg://", 1)

DATABASE_URL = URL

if not BOT_TOKEN:
    exit("Ошибка: BOT_TOKEN не найден в .env")
