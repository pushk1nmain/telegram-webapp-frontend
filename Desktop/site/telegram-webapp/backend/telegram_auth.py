import hashlib
import hmac
import json
from urllib.parse import unquote, parse_qsl
from typing import Optional, Dict
from config import settings

def validate_telegram_data(init_data: str, bot_token: str = None) -> Optional[Dict]:
    """
    Проверка подлинности данных от Telegram WebApp
    
    Args:
        init_data: Строка initData от Telegram WebApp
        bot_token: Токен бота (по умолчанию из config.py)
    
    Returns:
        Dict с данными пользователя если валидация прошла успешно, иначе None
    """
    if not bot_token:
        bot_token = settings.TELEGRAM_BOT_TOKEN
    
    if not bot_token or bot_token == "your_bot_token_here":
        print("⚠️ TELEGRAM_BOT_TOKEN не настроен в config.py")
        return None
    
    try:
        # Парсим данные
        parsed_data = dict(parse_qsl(unquote(init_data)))
        
        # Извлекаем hash
        received_hash = parsed_data.pop('hash', None)
        if not received_hash:
            return None
        
        # Создаем строку для проверки
        data_check_string = '\n'.join([f"{k}={v}" for k, v in sorted(parsed_data.items())])
        
        # Создаем ключ
        secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
        
        # Вычисляем hash
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        # Проверяем hash
        if calculated_hash != received_hash:
            print("❌ Telegram данные не прошли проверку hash")
            return None
        
        # Парсим данные пользователя
        user_data = json.loads(parsed_data.get('user', '{}'))
        
        return {
            'id': user_data.get('id'),
            'first_name': user_data.get('first_name'),
            'last_name': user_data.get('last_name'),
            'username': user_data.get('username'),
            'language_code': user_data.get('language_code'),
            'is_premium': user_data.get('is_premium', False),
            'auth_date': parsed_data.get('auth_date'),
            'query_id': parsed_data.get('query_id')
        }
        
    except Exception as e:
        print(f"❌ Ошибка валидации Telegram данных: {e}")
        return None

def extract_user_from_init_data(init_data: str) -> Optional[Dict]:
    """
    Извлечение данных пользователя без строгой проверки (для разработки)
    """
    try:
        parsed_data = dict(parse_qsl(unquote(init_data)))
        user_data = json.loads(parsed_data.get('user', '{}'))
        return user_data
    except:
        return None