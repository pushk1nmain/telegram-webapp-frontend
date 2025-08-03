from sqlalchemy import Column, Integer, String, Boolean, DateTime, Time, BigInteger, Index
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime, timezone, timedelta
from typing import Optional

Base = declarative_base()

# Московское время
MSK = timezone(timedelta(hours=3))

class User(Base):
    """Модель пользователя с современным подходом SQLAlchemy 2.0+"""
    __tablename__ = "users"
    
    # Современный синтаксис SQLAlchemy 2.0+
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    premium: Mapped[bool] = mapped_column(Boolean, default=False)
    progress_step: Mapped[int] = mapped_column(Integer, default=0)
    lesson: Mapped[int] = mapped_column(Integer, default=0)
    last_lesson: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    preferred_lesson_time: Mapped[Optional[datetime.time]] = mapped_column(Time, nullable=True)
    energy: Mapped[int] = mapped_column(Integer, default=100)
    certificate_price: Mapped[int] = mapped_column(Integer, default=9990)
    name: Mapped[str] = mapped_column(String, default="Друг")
    town: Mapped[str] = mapped_column(String, default="Чудесный город")
    letters_received: Mapped[int] = mapped_column(Integer, default=0)
    tz_offset: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(MSK),
        server_default=func.now()
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Индексы для оптимизации
    __table_args__ = (
        Index('idx_user_telegram_id', 'telegram_id'),
        Index('idx_user_active', 'is_active'),
        Index('idx_user_created', 'created_at'),
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, name='{self.name}')>"

    def to_dict(self) -> dict:
        """Преобразование объекта в словарь для JSON ответов"""
        return {
            'id': self.id,
            'username': self.username,
            'telegram_id': self.telegram_id,
            'premium': self.premium,
            'progress_step': self.progress_step,
            'lesson': self.lesson,
            'last_lesson': self.last_lesson.isoformat() if self.last_lesson else None,
            'preferred_lesson_time': self.preferred_lesson_time.strftime('%H:%M:%S') if self.preferred_lesson_time else None,
            'energy': self.energy,
            'certificate_price': self.certificate_price,
            'name': self.name,
            'town': self.town,
            'letters_received': self.letters_received,
            'tz_offset': self.tz_offset,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }
    
    @classmethod
    def create(cls, telegram_id: int, username: Optional[str] = None, premium: bool = False) -> "User":
        """Фабричный метод для создания пользователя"""
        return cls(
            telegram_id=telegram_id,
            username=username,
            premium=premium
        )