import asyncio
import logging
import sys
import os

# Ensure the root directory is in sys.path so 'src.*' imports work regardless of how python is called
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from src.config import BOT_TOKEN, WEBHOOK_URL
from src.database import init_db
from src.keep_alive import start_webhook_server
from src.services.scheduler import start_scheduler

# Routers
from src.handlers import common, dictionary, training, translator, settings

async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    # Initialize database with retries
    max_retries = 5
    for attempt in range(max_retries):
        try:
            logging.info(f"Database initialization attempt {attempt + 1}/{max_retries}...")
            await init_db()
            logging.info("Database initialized successfully.")
            break
        except Exception as e:
            if attempt == max_retries - 1:
                logging.error(f"Failed to initialize database after {max_retries} attempts: {e}")
                return
            logging.warning(f"Database init failed (will retry in 5s): {e}")
            await asyncio.sleep(5)
    
    try:
        bot = Bot(token=BOT_TOKEN)
        dp = Dispatcher(storage=MemoryStorage())
        
        # Start Scheduler
        start_scheduler(bot)
        
        # Include all routers
        dp.include_router(settings.router)
        dp.include_router(dictionary.router)
        dp.include_router(training.router)
        dp.include_router(translator.router)
        dp.include_router(common.router) # common should be last since it has fallback
        
        logging.info(f"Environment check - WEBHOOK_URL found: {bool(WEBHOOK_URL)}")
        
        if WEBHOOK_URL:
            logging.info(f"Configuring Webhook: {WEBHOOK_URL}")
            await bot.set_webhook(url=WEBHOOK_URL, drop_pending_updates=True)
            # Webhook server starts below and it's an async blocking call
            await start_webhook_server(bot, dp)
        else:
            logging.warning("WEBHOOK_URL not set! Falling back to Polling...")
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot)
            
    except Exception as e:
        logging.critical(f"FATAL ERROR: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.critical(f"Process exited with fatal error: {e}")
