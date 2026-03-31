import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from sqlalchemy import select
from src.database import async_session, Word

async def send_morning_message(bot: Bot):
    async with async_session() as session:
        result = await session.execute(select(Word.user_id).distinct())
        users = result.scalars().all()
        
    for user_id in users:
        try:
            await bot.send_message(user_id, "🌅 Доброе утро! Не забывай записывать новые английские слова! ✍️")
        except:
            pass

async def send_evening_message(bot: Bot):
    async with async_session() as session:
        result = await session.execute(select(Word.user_id).distinct())
        users = result.scalars().all()
        
    for user_id in users:
        try:
            await bot.send_message(user_id, "🌙 Добрый вечер! Мне кажется, самое время повторить изученные слова! 🎯")
        except:
            pass

def start_scheduler(bot: Bot):
    timezone = pytz.timezone("Europe/Warsaw")
    scheduler = AsyncIOScheduler(timezone=timezone)
    
    scheduler.add_job(send_morning_message, 'cron', hour=9, minute=0, args=[bot])
    scheduler.add_job(send_evening_message, 'cron', hour=21, minute=0, args=[bot])
    
    scheduler.start()
