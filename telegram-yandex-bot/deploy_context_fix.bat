@echo off
REM Скрипт для развертывания исправлений контекста на продакшене

echo 🚀 Развертывание исправлений контекста на продакшене
echo ==================================================

REM Проверяем, что мы в правильной директории
if not exist "docker-compose.yml" (
    echo ❌ Ошибка: docker-compose.yml не найден. Запустите скрипт из корневой директории проекта.
    pause
    exit /b 1
)

REM Останавливаем текущий контейнер
echo 🛑 Останавливаем текущий контейнер...
docker compose down

REM Пересобираем образ с исправлениями
echo 🔨 Пересобираем образ с исправлениями контекста...
docker compose build --no-cache

REM Запускаем обновленный контейнер
echo ▶️ Запускаем обновленный контейнер...
docker compose up -d

REM Ждем запуска
echo ⏳ Ждем запуска контейнера...
timeout /t 10 /nobreak > nul

REM Проверяем статус
echo 📊 Проверяем статус контейнера...
docker compose ps

REM Проверяем логи
echo 📝 Проверяем логи запуска...
docker compose logs bot --tail=20

REM Проверяем health check
echo 🏥 Проверяем health check...
curl -f http://localhost:11844/health 2>nul || echo ❌ Health check не прошел

echo.
echo ✅ Развертывание завершено!
echo.
echo 📋 Что было исправлено:
echo • Контекст теперь сохраняется в файл /app/logs/chat_contexts.json
echo • Контекст не теряется при перезапуске контейнера
echo • Улучшены fallback сообщения для случаев с существующим контекстом
echo • Добавлены отладочные логи для диагностики
echo.
echo 🧪 Для тестирования отправьте несколько сообщений в business чат
echo 📊 Логи можно проверить командой: docker compose logs bot --tail=50
echo 💾 Файл контекста: docker compose exec bot cat /app/logs/chat_contexts.json
echo.
pause
