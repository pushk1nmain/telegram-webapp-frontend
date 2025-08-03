// Конфигурация API для Telegram WebApp
const CONFIG = {
    // Режим отладки - отключает проверки Telegram
    DEBUG: true, // Установите false для продакшена
    
    // API URL - указывайте сюда адрес вашего сервера
    API_BASE_URL: (() => {
        const protocol = window.location.protocol;
        
        if (protocol === 'file:') {
            // Локальная разработка - к вашему серверу
            return 'https://webapp.smokybot.com/api/v1';
        } else if (window.location.hostname === 'localhost') {
            // Если запускаете локальный сервер для фронта
            return 'https://webapp.smokybot.com/api/v1';  
        } else {
            // Продакшен на Vercel - обращаемся к внешнему API
            return 'https://webapp.smokybot.com/api/v1';
        }
    })(),
    
    ENDPOINTS: {
        USERS: '/users',                    // POST для создания
        USER_UPDATE: "/users/{telegram_id}", // PATCH для обновления
        HEALTH: '/health'                   // GET для проверки
    },
    
    TELEGRAM: {
        BOT_USERNAME: 'smokyaibot', // Укажите username вашего бота
        initData: null,
        user: null,
        isExpanded: false
    }
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