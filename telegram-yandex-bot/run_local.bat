@echo off
echo 🤖 Запуск Telegram бота с YandexGPT...
echo 📝 Логирование всех входящих сообщений включено
echo 📁 Логи сохраняются в папке logs/
echo ------------------------------------------------

REM Проверяем наличие Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден! Установите Python 3.8+
    pause
    exit /b 1
)

REM Проверяем наличие .env файла
if not exist .env (
    echo ⚠️  Файл .env не найден!
    echo 📋 Скопируйте env.example в .env и заполните переменные:
    echo    copy env.example .env
    echo    # Затем отредактируйте .env файл
    pause
    exit /b 1
)

REM Устанавливаем зависимости если нужно
if not exist src\__pycache__ (
    echo 📦 Устанавливаем зависимости...
    pip install -r requirements.txt
)

REM Запускаем бота
python run_local.py

pause
