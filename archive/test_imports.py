import sys
sys.path.insert(0, ".")

import asyncio
from aiogram import Bot, Dispatcher
from src.config import BOT_TOKEN
from src.handlers import common, dictionary, training, translator, settings

async def main():
    print("Imports passed successfully!")

if __name__ == '__main__':
    asyncio.run(main())
