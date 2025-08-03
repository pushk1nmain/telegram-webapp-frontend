from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, time
import pytz
from sqlalchemy import text 

from database import get_db, create_tables
from models import User
from telegram_auth import validate_telegram_data, extract_user_from_init_data
from config import settings

# Создание приложения FastAPI
app = FastAPI(
    title="Telegram WebApp API",
    description="API для обучающего приложения в Telegram WebApp",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)

# Pydantic модели для API (обновлено для Pydantic 2.11+)
class UserCreate(BaseModel):
    telegram_id: int
    username: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    town: Optional[str] = Field(None, min_length=2, max_length=50)
    premium: Optional[bool] = None
    progress_step: Optional[int] = Field(None, ge=0)
    lesson: Optional[int] = Field(None, ge=0)
    preferred_lesson_time: Optional[time] = None
    energy: Optional[int] = Field(None, ge=0, le=100)
    tz_offset: Optional[int] = Field(None, ge=-12, le=12)

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # Новый синтаксис для Pydantic 2.11+
    
    id: int
    telegram_id: int
    username: Optional[str]
    name: str
    town: str
    premium: bool
    progress_step: int
    lesson: int
    energy: int
    letters_received: int
    created_at: datetime
    is_active: bool

# Dependency для проверки Telegram данных
async def verify_telegram_user(
    request: Request,
    x_telegram_init_data: Optional[str] = Header(None)
) -> dict:
    """Проверка аутентификации пользователя Telegram"""
    
    # В режиме разработки можем пропустить проверку
    if settings.DEBUG and not x_telegram_init_data:
        return {"id": 123456789, "username": "debug_user"}
    
    if not x_telegram_init_data:
        raise HTTPException(status_code=401, detail="Telegram данные не предоставлены")
    
    # Проверяем данные от Telegram
    user_data = validate_telegram_data(x_telegram_init_data)
    if not user_data:
        user_data = extract_user_from_init_data(x_telegram_init_data)
        if not user_data:
            raise HTTPException(status_code=401, detail="Невалидные Telegram данные")
    
    return user_data

# События жизненного цикла (обновлено для FastAPI 0.116+)
@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    try:
        create_tables()
        print("🚀 API сервер запущен")
        print(f"📊 Debug режим: {settings.DEBUG}")
        print(f"🗄️ База данных: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'local'}")
    except Exception as e:
        print(f"❌ Ошибка при запуске: {e}")
        raise

# Основные эндпоинты
@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Telegram WebApp API", 
        "status": "running", 
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/health")
async def health_check(db: Session = Depends(get_db)):
    """Проверка состояния API и базы данных"""
    try:
        result = db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "OK",
        "database": db_status,
        "timestamp": datetime.now(pytz.timezone(settings.TIMEZONE)).isoformat(),
        "debug": settings.DEBUG
    }

@app.post("/api/v1/users")
async def create_or_get_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    telegram_user: dict = Depends(verify_telegram_user)
):
    """Создание нового пользователя или получение существующего"""
    
    if user_data.telegram_id != telegram_user.get("id"):
        raise HTTPException(status_code=403, detail="Несоответствие telegram_id")
    
    try:
        existing_user = db.query(User).filter(User.telegram_id == user_data.telegram_id).first()
        
        if existing_user:
            return {
                "success": True,
                "message": "Пользователь найден",
                "user": existing_user.to_dict(),
                "created": False
            }
        
        new_user = User(
            telegram_id=user_data.telegram_id,
            username=user_data.username or telegram_user.get("username"),
            premium=telegram_user.get("is_premium", False)
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"✅ Новый пользователь создан: {new_user.telegram_id} - {new_user.name}")
        
        return {
            "success": True,
            "message": "Пользователь создан",
            "user": new_user.to_dict(),
            "created": True
        }
        
    except IntegrityError:
        db.rollback()
        existing_user = db.query(User).filter(User.telegram_id == user_data.telegram_id).first()
        return {
            "success": True,
            "message": "Пользователь уже существует",
            "user": existing_user.to_dict() if existing_user else None,
            "created": False
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка создания пользователя: {str(e)}")

@app.patch("/api/v1/users/{telegram_id}")
async def update_user(
    telegram_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    telegram_user: dict = Depends(verify_telegram_user)
):
    """Обновление данных пользователя"""
    
    if telegram_id != telegram_user.get("id"):
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Используем model_dump для Pydantic 2.11+
    update_data = user_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    try:
        db.commit()
        db.refresh(user)
        
        print(f"✅ Пользователь обновлен: {user.telegram_id} - {user.name}")
        
        return {
            "success": True,
            "message": "Данные обновлены",
            "user": user.to_dict()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка обновления: {str(e)}")

@app.get("/api/v1/users/{telegram_id}", response_model=UserResponse)
async def get_user(
    telegram_id: int,
    db: Session = Depends(get_db),
    telegram_user: dict = Depends(verify_telegram_user)
):
    """Получение данных пользователя"""
    
    if telegram_id != telegram_user.get("id"):
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    return user

@app.get("/api/v1/users", response_model=List[UserResponse])
async def get_all_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Получение списка всех пользователей (для админки)"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

# Запуск сервера
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )