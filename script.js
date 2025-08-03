// Telegram WebApp интеграция
let currentBlock = 0;
let telegramUser = null;
let userData = {
    name: '',
    town: '',
    telegram_id: null,
    username: null
};

// Инициализация Telegram WebApp
function initTelegramWebApp() {
    if (typeof Telegram !== 'undefined' && Telegram.WebApp) {
        const webapp = Telegram.WebApp;
        
        // Расширяем WebApp на весь экран
        webapp.expand();
        
        // Включаем кнопку закрытия
        webapp.enableClosingConfirmation();
        
        // Настраиваем цвета под тему Telegram
        webapp.setHeaderColor(webapp.themeParams.bg_color || '#ffffff');
        
        // Получаем данные пользователя
        if (webapp.initDataUnsafe && webapp.initDataUnsafe.user) {
            telegramUser = webapp.initDataUnsafe.user;
            userData.telegram_id = telegramUser.id;
            userData.username = telegramUser.username || '';
            
            console.log('Telegram User:', telegramUser);
            
            // Показываем информацию о пользователе (для отладки)
            const userIdElement = document.getElementById('userId');
            if (userIdElement) {
                userIdElement.textContent = telegramUser.id;
                document.getElementById('webAppInfo').style.display = 'block';
            }
            
            // Автоматически создаем/обновляем пользователя в БД
            createOrUpdateUser();
        }
        
        // Обработчик кнопки "Назад" в Telegram
        webapp.onEvent('backButtonClicked', () => {
            if (currentBlock > 0) {
                handleButtonClick('prev');
            } else {
                webapp.close();
            }
        });
        
        CONFIG.TELEGRAM = {
            initData: webapp.initData,
            user: telegramUser,
            isExpanded: webapp.isExpanded
        };
        
    } else {
        console.warn('Telegram WebApp SDK не найден. Работаем в режиме отладки.');
        // Для тестирования без Telegram
        userData.telegram_id = Date.now(); // Временный ID
    }
}

// Создание или обновление пользователя в БД
async function createOrUpdateUser() {
    if (!userData.telegram_id) return;
    
    try {
        const response = await fetch(getApiUrl(CONFIG.ENDPOINTS.USERS), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Telegram-Init-Data': CONFIG.TELEGRAM.initData || ''
            },
            body: JSON.stringify({
                telegram_id: userData.telegram_id,
                username: userData.username
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('Пользователь создан/обновлен:', result);
            
            // Если у пользователя уже есть имя, заполняем
            if (result.user.name && result.user.name !== 'Друг') {
                userData.name = result.user.name;
            }
            if (result.user.town && result.user.town !== 'Чудесный город') {
                userData.town = result.user.town;
            }
        }
    } catch (error) {
        console.error('Ошибка создания пользователя:', error);
    }
}

// Отрисовка блока контента
function renderBlock(blockIndex) {
    const block = courseData.blocks[blockIndex];
    const textContent = document.getElementById('textContent');
    const buttonsContainer = document.getElementById('buttonsContainer');
    const courseImage = document.getElementById('courseImage');
    
    // Персонализированный заголовок
    let title = block.title;
    if (userData.name && blockIndex > 0) {
        title = title.replace('Отлично!', `Отлично, ${userData.name}!`);
    }
    
    // Обновляем контент в зависимости от типа блока
    if (block.type === 'name_input') {
        textContent.innerHTML = `
            <h2>${title}</h2>
            <p>${block.text}</p>
            <div class="input-container">
                <input type="text" id="nameInput" class="input-field" 
                       placeholder="Ваше имя..." 
                       value="${userData.name}"
                       maxlength="50" />
                <div class="input-error" id="inputError" style="display: none;"></div>
            </div>
        `;
    } else if (block.type === 'town_input') {
        textContent.innerHTML = `
            <h2>${title}</h2>
            <p>${block.text}</p>
            <div class="input-container">
                <input type="text" id="townInput" class="input-field" 
                       placeholder="Ваш город..." 
                       value="${userData.town}"
                       maxlength="50" />
                <div class="input-error" id="townError" style="display: none;"></div>
            </div>
        `;
    } else {
        textContent.innerHTML = `
            <h2>${title}</h2>
            <p>${block.text}</p>
        `;
    }
    
    // Обновляем изображение
    courseImage.innerHTML = '';
    
    if (block.image && block.image.startsWith('http')) {
        const img = document.createElement('img');
        img.src = block.image;
        img.onerror = () => {
            courseImage.innerHTML = `<div class="course-image-placeholder">${block.placeholder || '🖼️'}</div>`;
        };
        courseImage.appendChild(img);
    } else {
        courseImage.innerHTML = `<div class="course-image-placeholder">${block.placeholder || '🖼️'}</div>`;
    }
    
    // Обновляем кнопки
    buttonsContainer.innerHTML = '';
    block.buttons.forEach(button => {
        const btn = document.createElement('button');
        btn.className = 'btn';
        btn.textContent = button.text;
        btn.onclick = () => handleButtonClick(button.action);
        buttonsContainer.appendChild(btn);
    });
    
    // Обновляем индикаторы прогресса
    updateProgressIndicator();
    
    // Фокус на поля ввода
    setTimeout(() => {
        const nameInput = document.getElementById('nameInput');
        const townInput = document.getElementById('townInput');
        if (nameInput) nameInput.focus();
        if (townInput) townInput.focus();
    }, 100);
}

// Обновление индикаторов прогресса
function updateProgressIndicator() {
    const progressIndicator = document.getElementById('progressIndicator');
    progressIndicator.innerHTML = '';
    
    courseData.blocks.forEach((_, index) => {
        const dot = document.createElement('div');
        dot.className = `progress-dot ${index === currentBlock ? 'active' : ''}`;
        progressIndicator.appendChild(dot);
    });
}

// Сохранение имени
async function submitName() {
    const nameInput = document.getElementById('nameInput');
    const inputError = document.getElementById('inputError');
    const name = nameInput.value.trim();
    
    if (!name || name.length < 2) {
        inputError.textContent = 'Введите имя (минимум 2 символа)';
        inputError.style.display = 'block';
        nameInput.focus();
        return;
    }
    
    inputError.style.display = 'none';
    
    try {
        const btn = document.querySelector('.btn');
        const originalText = btn.textContent;
        btn.textContent = 'Сохраняем...';
        btn.disabled = true;
        
        const response = await fetch(getApiUrl(CONFIG.ENDPOINTS.USER_UPDATE, { telegram_id: userData.telegram_id }), {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-Telegram-Init-Data': CONFIG.TELEGRAM.initData || ''
            },
            body: JSON.stringify({ name: name })
        });
        
        if (response.ok) {
            userData.name = name;
            currentBlock++;
            renderBlock(currentBlock);
        } else {
            throw new Error('Ошибка сохранения');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        inputError.textContent = 'Ошибка сохранения. Попробуйте еще раз.';
        inputError.style.display = 'block';
        
        const btn = document.querySelector('.btn');
        btn.textContent = originalText;
        btn.disabled = false;
    }
}

// Сохранение города
async function submitTown() {
    const townInput = document.getElementById('townInput');
    const townError = document.getElementById('townError');
    const town = townInput.value.trim();
    
    if (!town || town.length < 2) {
        townError.textContent = 'Введите город (минимум 2 символа)';
        townError.style.display = 'block';
        townInput.focus();
        return;
    }
    
    townError.style.display = 'none';
    
    try {
        const btn = document.querySelector('.btn');
        const originalText = btn.textContent;
        btn.textContent = 'Сохраняем...';
        btn.disabled = true;
        
        const response = await fetch(getApiUrl(CONFIG.ENDPOINTS.USER_UPDATE, { telegram_id: userData.telegram_id }), {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-Telegram-Init-Data': CONFIG.TELEGRAM.initData || ''
            },
            body: JSON.stringify({ town: town })
        });
        
        if (response.ok) {
            userData.town = town;
            currentBlock++;
            renderBlock(currentBlock);
        } else {
            throw new Error('Ошибка сохранения');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        townError.textContent = 'Ошибка сохранения. Попробуйте еще раз.';
        townError.style.display = 'block';
        
        const btn = document.querySelector('.btn');
        btn.textContent = originalText;
        btn.disabled = false;
    }
}

// Обработчик действий кнопок
function handleButtonClick(action) {
    switch(action) {
        case 'submit_name':
            submitName();
            break;
        case 'submit_town':
            submitTown();
            break;
        case 'next':
            if (currentBlock < courseData.blocks.length - 1) {
                currentBlock++;
                renderBlock(currentBlock);
            }
            break;
        case 'prev':
            if (currentBlock > 0) {
                currentBlock--;
                renderBlock(currentBlock);
            }
            break;
        case 'start_lesson':
            if (Telegram.WebApp) {
                Telegram.WebApp.showAlert('Переход к урокам! 🚀');
            } else {
                alert('Переход к урокам! 🚀');
            }
            break;
        case 'settings':
            if (Telegram.WebApp) {
                Telegram.WebApp.showAlert('Настройки пользователя');
            } else {
                alert('Настройки пользователя');
            }
            break;
    }
}

// Инициализация приложения при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM загружен, начинаем инициализацию...');
    
    // Инициализируем Telegram WebApp
    initTelegramWebApp();
    
    // Отрисовываем первый блок контента
    renderBlock(currentBlock);
    
    console.log('Инициализация завершена');
});

// Поддержка клавиатуры
document.addEventListener('keydown', function(e) {
    if (document.activeElement && document.activeElement.tagName === 'INPUT') {
        if (e.key === 'Enter') {
            const currentAction = courseData.blocks[currentBlock].buttons[0].action;
            handleButtonClick(currentAction);
        }
        return;
    }
    
    if (e.key === 'ArrowRight' || e.key === ' ') {
        e.preventDefault();
        handleButtonClick('next');
    } else if (e.key === 'ArrowLeft') {
        e.preventDefault();
        handleButtonClick('prev');
    }
});