from sqlalchemy import select, delete, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import User, Word
from datetime import datetime, timedelta

async def get_or_create_user(session: AsyncSession, user_id: int):
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        user = User(id=user_id)
        session.add(user)
        await session.commit()
    return user

async def add_word(session: AsyncSession, user_id: int, original: str, translated: str):
    new_word = Word(
        user_id=user_id,
        original_text=original,
        translated_text=translated,
        status="learning"
    )
    session.add(new_word)
    await session.commit()
    return new_word

async def get_words_count(session: AsyncSession, user_id: int, status: str, days: int = None):
    query = select(func.count(Word.id)).where(Word.user_id == user_id, Word.status == status)
    
    if days is not None:
        since = datetime.utcnow() - timedelta(days=days)
        query = query.where(Word.created_at >= since)
        
    result = await session.execute(query)
    return result.scalar()

async def get_user_words(session: AsyncSession, user_id: int, status: str):
    result = await session.execute(
        select(Word).where(Word.user_id == user_id, Word.status == status)
    )
    return result.scalars().all()
