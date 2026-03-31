from sqlalchemy import Column, BigInteger, String, Integer, ForeignKey, DateTime
from datetime import datetime
from src.database.instance import Base

class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True) # Telegram ID пользователя

class Word(Base):
    __tablename__ = "words"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    original_text = Column(String)
    translated_text = Column(String)
    status = Column(String, default="learning") # 'learning' или 'learned'
    created_at = Column(DateTime, default=datetime.utcnow)
