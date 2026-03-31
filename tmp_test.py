import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database import init_db, add_word, get_user

async def main():
    await init_db()
    # User 123 doesn't exist
    try:
        await add_word(1234567, "test", "test", "en")
        print("Success")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(main())
