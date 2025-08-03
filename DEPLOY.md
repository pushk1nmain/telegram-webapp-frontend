# Деплой Telegram WebApp на Vercel

## Пошаговая инструкция

### 1. Подготовка проекта

Ваш проект уже настроен для деплоя на Vercel:
- ✅ `vercel.json` - конфигурация для Vercel
- ✅ `.vercelignore` - файлы для игнорирования
- ✅ `package.json` - обновлен со скриптом деплоя

### 2. Создание GitHub репозитория

1. Зайдите на [GitHub](https://github.com) и создайте новый репозиторий
2. Назовите его, например: `telegram-webapp-course`
3. Сделайте репозиторий публичным (для бесплатного Vercel)

### 3. Загрузка кода в GitHub

Выполните в терминале из папки вашего проекта:

```bash
# Инициализация git (если не сделано)
git init

# Добавление всех файлов
git add .

# Первый коммит
git commit -m "Initial commit: Telegram WebApp frontend"

# Добавление remote репозитория
git remote add origin https://github.com/ВАШ_USERNAME/telegram-webapp-course.git

# Загрузка на GitHub
git branch -M main
git push -u origin main
```

### 4. Деплой на Vercel

#### Вариант A: Через веб-интерфейс (рекомендуемый)

1. Зайдите на [vercel.com](https://vercel.com)
2. Войдите через GitHub аккаунт
3. Нажмите "New Project"
4. Выберите ваш репозиторий `telegram-webapp-course`
5. В настройках проекта:
   - **Framework Preset**: Other
   - **Root Directory**: `telegram-webapp/frontend`
   - **Build Command**: оставьте пустым
   - **Output Directory**: `./`
6. Нажмите "Deploy"

#### Вариант B: Через Vercel CLI

```bash
# Установка Vercel CLI
npm i -g vercel

# Деплой (из папки telegram-webapp/frontend)
cd telegram-webapp/frontend
vercel --prod
```

### 5. Получение HTTPS URL

После успешного деплоя вы получите URL вида:
- `https://telegram-webapp-course.vercel.app`
- или с вашим доменом: `https://ваш-проект.vercel.app`

### 6. Обновление Telegram бота

В коде вашего Telegram бота замените локальный URL:

```python
# Старый код
web_app = WebAppInfo(url="http://localhost:3000/")

# Новый код
web_app = WebAppInfo(url="https://ваш-проект.vercel.app/")
```

### 7. Автоматическое обновление

После настройки каждое обновление кода в GitHub будет автоматически деплоиться на Vercel:

1. Внесите изменения в код
2. Сделайте commit и push:
   ```bash
   git add .
   git commit -m "Описание изменений"
   git push
   ```
3. Vercel автоматически обновит сайт

### 8. Дополнительные настройки

#### Пользовательский домен (опционально)
- В панели Vercel перейдите в Settings → Domains
- Добавьте свой домен

#### Переменные окружения (если нужны)
- В панели Vercel перейдите в Settings → Environment Variables
- Добавьте нужные переменные

## Полезные команды

```bash
# Локальная разработка
npm run dev

# Деплой на production
npm run deploy  # или vercel --prod

# Просмотр логов деплоя
vercel logs
```

## Проверка работы

1. Откройте ваш HTTPS URL в браузере
2. Убедитесь, что приложение загружается
3. Протестируйте в Telegram боте
4. Проверьте, что все функции работают

## Поддержка

Если возникли проблемы:
- Проверьте логи в панели Vercel
- Убедитесь, что все файлы загружены в GitHub
- Проверьте настройки Root Directory в Vercel

---

**Готово!** Ваше приложение теперь доступно по HTTPS и будет автоматически обновляться при изменениях в коде. 