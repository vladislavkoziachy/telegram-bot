from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import Integer, String, BigInteger, select, update, delete, DateTime, ForeignKey
from datetime import datetime

from src.config import DATABASE_URL

engine = create_async_engine(
    DATABASE_URL, 
    echo=False,
    pool_pre_ping=True,
    connect_args={"statement_cache_size": 0} 
)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True) # Telegram ID
    interface_lang: Mapped[str] = mapped_column(String, default="ru")
    learning_lang: Mapped[str] = mapped_column(String, default="en")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Word(Base):
    __tablename__ = "words"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    learning_lang: Mapped[str] = mapped_column(String, default="en") # Which language this word belongs to
    word: Mapped[str] = mapped_column(String)
    translation: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="learning") # 'learning' or 'learned'
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    learned_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Attempt to add learned_at column if it's missing from previous DB versions
        from sqlalchemy import text
        try:
            await conn.execute(text("ALTER TABLE words ADD COLUMN learned_at DATETIME;"))
        except Exception:
            pass

# User Helpers
async def get_user(user_id: int) -> User | None:
    async with async_session() as session:
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        return result.scalars().first()

async def create_user(user_id: int, interface_lang: str = "ru", learning_lang: str = "en"):
    async with async_session() as session:
        user = User(id=user_id, interface_lang=interface_lang, learning_lang=learning_lang)
        session.add(user)
        await session.commit()
        return user

async def update_user(user_id: int, **kwargs):
    async with async_session() as session:
        stmt = update(User).where(User.id == user_id).values(**kwargs)
        await session.execute(stmt)
        await session.commit()

# CRUD Helpers (Word)
async def add_word(user_id: int, word: str, translation: str, learning_lang: str) -> bool:
    """Returns False if word already exists for user and language, True if added."""
    async with async_session() as session:
        stmt = select(Word).where(
            Word.user_id == user_id, 
            Word.word == word, 
            Word.learning_lang == learning_lang
        )
        result = await session.execute(stmt)
        if result.scalars().first():
            return False
            
        new_word = Word(
            user_id=user_id, 
            word=word, 
            translation=translation, 
            learning_lang=learning_lang, 
            status="learning"
        )
        session.add(new_word)
        await session.commit()
        return True

async def get_words(user_id: int, learning_lang: str, status: str = None, since: datetime = None) -> list[Word]:
    """Returns a list of Word objects for the user and specific language."""
    async with async_session() as session:
        stmt = select(Word).where(Word.user_id == user_id, Word.learning_lang == learning_lang)
        if status:
            stmt = stmt.where(Word.status == status)
        if since and status == "learned":
            stmt = stmt.where(Word.learned_at >= since)
        stmt = stmt.order_by(Word.id.desc())
        result = await session.execute(stmt)
        return list(result.scalars().all())

async def count_words(user_id: int, learning_lang: str, status: str = None, since: datetime = None) -> int:
    """Returns count of words."""
    words = await get_words(user_id, learning_lang, status, since)
    return len(words)

async def update_word_status(user_id: int, learning_lang: str, word: str, new_status: str):
    async with async_session() as session:
        updates = {"status": new_status}
        if new_status == "learned":
            updates["learned_at"] = datetime.utcnow()
            
        stmt = update(Word).where(
            Word.user_id == user_id, 
            Word.word == word,
            Word.learning_lang == learning_lang
        ).values(**updates)
        await session.execute(stmt)
        await session.commit()

async def delete_word(user_id: int, learning_lang: str, word: str):
    async with async_session() as session:
        stmt = delete(Word).where(
            Word.user_id == user_id, 
            Word.word == word,
            Word.learning_lang == learning_lang
        )
        await session.execute(stmt)
        await session.commit()
