from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from src.config import DATABASE_URL

# Создаем движок (двигатель) для общения с SQLite
engine = create_async_engine(DATABASE_URL, echo=False)

# Создаем сессию — это как "открытый канал" связи с базой
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Базовый класс для всех наших таблиц
Base = declarative_base()

async def init_db():
    async with engine.begin() as conn:
        # Эта команда создаст все таблицы, если их еще нет
        await conn.run_sync(Base.metadata.create_all)
