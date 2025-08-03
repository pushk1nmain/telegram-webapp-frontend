from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from contextlib import contextmanager
from typing import Generator
import logging

from models import Base
from config import settings

# Настройка логирования
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Создание движка базы данных с оптимизированными настройками
engine: Engine = create_engine(
    settings.DATABASE_URL_SYNC,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=True,
    echo=settings.DEBUG,
    # Современные настройки для PostgreSQL
    connect_args={
        "options": "-c timezone=Europe/Moscow"
    }
)

# Фабрика сессий
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False  # Для лучшей производительности
)

def create_tables() -> None:
    """Создание всех таблиц в базе данных"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Таблицы созданы успешно")
    except Exception as e:
        logger.error(f"❌ Ошибка создания таблиц: {e}")
        raise

def drop_tables() -> None:
    """Удаление всех таблиц (для тестирования)"""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("🗑️ Таблицы удалены")
    except Exception as e:
        logger.error(f"❌ Ошибка удаления таблиц: {e}")
        raise

def get_db() -> Generator:
    """Генератор сессий базы данных для FastAPI Depends"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"❌ Ошибка в сессии БД: {e}")
        db.rollback()
        raise
    finally:
        db.close()

@contextmanager
def get_db_session():
    """Контекстный менеджер для работы с БД вне FastAPI"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        logger.error(f"❌ Ошибка в сессии БД: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def test_connection() -> bool:
    """Тестирование подключения к базе данных"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            conn.commit()
        logger.info("✅ Подключение к базе данных успешно")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к БД: {e}")
        return False

def get_db_info() -> dict:
    """Получение информации о базе данных"""
    try:
        with engine.connect() as conn:
            # Версия PostgreSQL
            version_result = conn.execute(text("SELECT version()"))
            version = version_result.scalar()
            
            # Количество подключений
            connections_result = conn.execute(text(
                "SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"
            ))
            active_connections = connections_result.scalar()
            
            # Размер базы данных
            db_name = settings.DATABASE_URL_SYNC.split('/')[-1]
            size_result = conn.execute(text(
                f"SELECT pg_size_pretty(pg_database_size('{db_name}'))"
            ))
            db_size = size_result.scalar()
            
            return {
                "version": version,
                "active_connections": active_connections,
                "database_size": db_size,
                "status": "connected"
            }
    except Exception as e:
        logger.error(f"❌ Ошибка получения информации о БД: {e}")
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    logger.info("🔄 Тестирование подключения к БД...")
    if test_connection():
        create_tables()
        print("📊 Информация о БД:")
        import json
        print(json.dumps(get_db_info(), indent=2, ensure_ascii=False))
    else:
        logger.error("💡 Проверьте настройки DATABASE_URL в config.py")