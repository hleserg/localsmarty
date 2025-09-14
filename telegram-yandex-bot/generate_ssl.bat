@echo off
echo 🔐 Генерация SSL сертификатов для Telegram Bot Webhook
echo ==================================================

REM Создаем директорию для SSL сертификатов
if not exist ssl mkdir ssl

REM Генерируем приватный ключ
echo 📝 Генерируем приватный ключ...
openssl genrsa -out ssl\key.pem 2048

REM Генерируем самоподписанный сертификат
echo 📜 Генерируем самоподписанный сертификат...
openssl req -new -x509 -key ssl\key.pem -out ssl\cert.pem -days 365 -subj "/C=RU/ST=Moscow/L=Moscow/O=TelegramBot/OU=IT/CN=localhost"

echo ✅ SSL сертификаты созданы:
echo    📄 ssl\cert.pem - сертификат
echo    🔑 ssl\key.pem - приватный ключ
echo.
echo ⚠️  ВНИМАНИЕ: Это самоподписанные сертификаты для разработки!
echo    Для продакшена используйте сертификаты от Let's Encrypt или другого CA
echo.
echo 🚀 Теперь можно запустить бота:
echo    docker compose up -d
pause
