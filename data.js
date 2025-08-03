// Данные контента для Telegram WebApp
const courseData = {
    blocks: [
        {
            title: "Добро пожаловать! 🤖",
            text: "Привет! Я ваш виртуальный помощник в изучении. Давайте знакомиться! Как вас зовут?",
            image: "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80",
            placeholder: "🤖",
            type: "name_input",
            buttons: [
                { text: "Сохранить имя", action: "submit_name" }
            ]
        },
        {
            title: "Отлично! 👋", 
            text: "Теперь давайте укажем ваш город для персонализации обучения.",
            placeholder: "🏙️",
            type: "town_input",
            buttons: [
                { text: "Сохранить город", action: "submit_town" }
            ]
        },
        {
            title: "Готовы начать обучение? 🚀",
            text: "У вас есть все необходимое для успешного прохождения курса. Ваш прогресс будет сохранен автоматически!",
            placeholder: "📚",
            buttons: [
                { text: "Начать урок 1", action: "start_lesson" },
                { text: "Настройки", action: "settings" }
            ]
        }
    ]
};

// Конфигурация API для Telegram WebApp
const CONFIG = {
    // Определяем среду
    API_BASE_URL: (() => {
        const protocol = window.location.protocol;
        
        if (protocol === 'file:') {
            // Локальная разработка - прямо к вашему API серверу
            return 'https://webapp.smokybot.com/api/v1';
        } else if (window.location.hostname === 'localhost') {
            // Локальный сервер для разработки
            return 'https://webapp.smokybot.com/api/v1';  
        } else {
            // Продакшен - через nginx
            return '/api/v1';
        }
    })(),
    
    ENDPOINTS: {
        USERS: '/users',
        USER_UPDATE: '/users/{telegram_id}',
        HEALTH: '/health'
    },
    
    TELEGRAM: {
        BOT_USERNAME: 'smokyaibot',
        initData: null,
        user: null,
        isExpanded: false
    },
    
    // Режим разработки
    DEBUG: window.location.protocol === 'file:' || window.location.hostname === 'localhost'
};

// Получение полного URL API
function getApiUrl(endpoint, params = {}) {
    let url = `${CONFIG.API_BASE_URL}${endpoint}`;
    
    // Замена параметров в URL (например {telegram_id})
    Object.keys(params).forEach(key => {
        url = url.replace(`{${key}}`, params[key]);
    });
    
    return url;
}

// Проверка доступа через Telegram
function checkTelegramAccess() {
    // В режиме разработки разрешаем доступ для тестирования
    if (CONFIG.DEBUG) {
        console.log('🛠️ Режим разработки: проверка Telegram отключена');
        return true;
    }
    
    // Проверка Telegram WebApp API
    if (typeof Telegram === 'undefined' || !Telegram.WebApp) {
        showTelegramError('Telegram WebApp API недоступен');
        return false;
    }
    
    // Проверка initData
    const initData = Telegram.WebApp.initData;
    if (!initData || initData.length === 0) {
        showTelegramError('Отсутствуют данные авторизации Telegram');
        return false;
    }
    
    return true;
}

// Показ ошибки доступа
function showTelegramError(reason = 'Неизвестная ошибка') {
    document.body.innerHTML = `
        <div style="
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            padding: 20px;
        ">
            <div style="
                background: rgba(255,255,255,0.1);
                padding: 40px;
                border-radius: 20px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.2);
                max-width: 400px;
            ">
                <h1 style="margin: 0 0 20px 0; font-size: 24px;">🤖 Доступ ограничен</h1>
                <p style="margin: 0 0 10px 0; font-size: 16px; line-height: 1.5;">
                    Это приложение можно использовать только через Telegram бот.
                </p>
                <p style="margin: 0 0 30px 0; font-size: 14px; color: rgba(255,255,255,0.8);">
                    Причина: ${reason}
                </p>
                <a href="https://t.me/${CONFIG.TELEGRAM.BOT_USERNAME}" 
                   style="
                       display: inline-block;
                       background: #0088cc;
                       color: white;
                       padding: 12px 24px;
                       border-radius: 25px;
                       text-decoration: none;
                       font-weight: bold;
                       transition: background 0.3s;
                   "
                   onmouseover="this.style.background='#0077bb'"
                   onmouseout="this.style.background='#0088cc'">
                    🚀 Открыть @${CONFIG.TELEGRAM.BOT_USERNAME}
                </a>
            </div>
        </div>
    `;
}

console.log('🔧 CONFIG загружен:', CONFIG);

// Проверка доступа при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Запуск приложения...');
    
    // Проверяем доступ через Telegram (в режиме разработки пропускается)
    if (!checkTelegramAccess()) {
        return; // Прекращаем выполнение если доступ запрещен
    }
    
    console.log('✅ Проверка доступа пройдена');
    
    // Даем время Telegram WebApp API загрузиться
    setTimeout(() => {
        initTelegramWebApp();
        renderBlock(currentBlock);
    }, 100);
});