import os
from typing import List
from pathlib import Path

class Settings:
    """Конфигурация приложения с последними стандартами"""
    
    # Базовый путь проекта
    BASE_DIR: Path = Path(__file__).resolve().parent
    
    # База данных PostgreSQL
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+asyncpg://smoky_user:eAqR*V0BPerQ@10.16.0.2:5432/smoky_db"
    )
    
    # Синхронная версия для совместимости
    DATABASE_URL_SYNC: str = os.getenv(
        "DATABASE_URL_SYNC",
        "postgresql://smoky_user:eAqR*V0BPerQ@10.16.0.2:5432/smoky_db"
    )
    
    # Настройки сервера
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    RELOAD: bool = os.getenv("RELOAD", "True").lower() == "true"
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "7695318446:AAFvXzA1K2U0AWvpHFF3vY1-e3peozpeekM")
    
    # Безопасность
    SECRET_KEY: str = os.getenv("SECRET_KEY", "jY3EHw7qMPhG4q22LFN5WnW4CiQWaK-3Gv76EVaRZ1W_9ZFbbsxJVLWc8RtRvnjc_kM5xPSrYRAbxN1uk7ysig")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "null",  # ← Для file:// протокола (локальная разработка)
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "https://webapp.smokybot.com",  # ← Ваш домен
        "http://webapp.smokybot.com",   # ← HTTP версия
        "*"  # ← Для максимальной совместимости в разработке
    ]
    
    # Логирование
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Timezone
    TIMEZONE: str = "Europe/Moscow"
    
    # Настройки базы данных
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600
    
    # API настройки
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Telegram WebApp API"
    PROJECT_VERSION: str = "2.0.0"
    
    class Config:
        case_sensitive = True

# Создаем экземпляр настроек
settings = Settings()