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

async def get_user_words(session: AsyncSession, user_id: int, status: str, days: int = None):
    query = select(Word).where(Word.user_id == user_id, Word.status == status)
    if days is not None:
        since = datetime.utcnow() - timedelta(days=days)
        query = query.where(Word.created_at >= since)
    
    result = await session.execute(query)
    return result.scalars().all()

async def delete_word(session: AsyncSession, word_id: int):
    await session.execute(delete(Word).where(Word.id == word_id))
    await session.commit()

async def update_word_status(session: AsyncSession, word_id: int, new_status: str):
    await session.execute(
        update(Word).where(Word.id == word_id).values(status=new_status)
    )
    await session.commit()

async def get_word_by_id(session: AsyncSession, word_id: int):
    result = await session.execute(select(Word).where(Word.id == word_id))
    return result.scalar_one_or_none()

async def get_word_by_text(session: AsyncSession, user_id: int, text: str):
    """Поиск слова по тексту (игнорируя регистр)."""
    query = select(Word).where(
        Word.user_id == user_id,
        func.lower(Word.original_text) == func.lower(text)
    )
    result = await session.execute(query)
    return result.scalar_one_or_none()
