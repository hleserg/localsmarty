#!/bin/bash

# Скрипт для генерации SSL сертификатов для webhook

echo "🔐 Генерация SSL сертификатов для Telegram Bot Webhook"
echo "=================================================="

# Создаем директорию для SSL сертификатов
mkdir -p ssl

# Генерируем приватный ключ
echo "📝 Генерируем приватный ключ..."
openssl genrsa -out ssl/key.pem 2048

# Генерируем самоподписанный сертификат
echo "📜 Генерируем самоподписанный сертификат..."
openssl req -new -x509 -key ssl/key.pem -out ssl/cert.pem -days 365 -subj "/C=RU/ST=Moscow/L=Moscow/O=TelegramBot/OU=IT/CN=localhost"

# Устанавливаем правильные права доступа
chmod 600 ssl/key.pem
chmod 644 ssl/cert.pem

echo "✅ SSL сертификаты созданы:"
echo "   📄 ssl/cert.pem - сертификат"
echo "   🔑 ssl/key.pem - приватный ключ"
echo ""
echo "⚠️  ВНИМАНИЕ: Это самоподписанные сертификаты для разработки!"
echo "   Для продакшена используйте сертификаты от Let's Encrypt или другого CA"
echo ""
echo "🚀 Теперь можно запустить бота:"
echo "   docker compose up -d"
