@echo off
echo 🚀 Развертывание Telegram Bot на talkbot.skhlebnikov.ru
echo ======================================================

REM Проверяем наличие Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker не установлен. Установите Docker и попробуйте снова.
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose не установлен. Установите Docker Compose и попробуйте снова.
    pause
    exit /b 1
)

echo ✅ Docker и Docker Compose найдены

REM Создаем .env если его нет
if not exist .env (
    echo 📝 Создаем файл .env из примера...
    copy env.example .env
    echo ⚠️  ВНИМАНИЕ: Отредактируйте файл .env с вашими токенами!
    echo    - TELEGRAM_TOKEN
    echo    - NEUROAPI_API_KEY
    echo    - WEBHOOK_SECRET_TOKEN
    echo.
    pause
)

REM SSL сертификаты не нужны - обрабатываются Hestia
echo ✅ SSL сертификаты обрабатываются Hestia - генерация не нужна

REM Создаем директории
echo 📁 Создаем необходимые директории...
if not exist logs mkdir logs

REM Останавливаем старые контейнеры
echo 🛑 Останавливаем старые контейнеры...
docker compose down

REM Собираем и запускаем новые контейнеры
echo 🔨 Собираем и запускаем контейнеры...
docker compose up -d --build

REM Ждем запуска
echo ⏳ Ждем запуска сервисов...
timeout /t 10 /nobreak >nul

REM Проверяем статус
echo 📊 Проверяем статус сервисов...
docker compose ps

echo.
echo 🎉 Развертывание завершено!
echo.
echo 📋 Информация о развертывании:
echo    🌐 Домен: talkbot.skhlebnikov.ru
echo    🔗 Webhook URL: https://talkbot.skhlebnikov.ru/bot
echo    🔌 Порт: 11844
echo    ❤️ Health check: https://talkbot.skhlebnikov.ru/health
echo.
echo 📝 Полезные команды:
echo    Логи: docker compose logs -f bot
echo    Статус: docker compose ps
echo    Перезапуск: docker compose restart bot
echo    Остановка: docker compose down
echo.
echo 🔍 Проверьте работу бота, отправив сообщение в Telegram!
pause
