#!/bin/bash

# Скрипт для установки webhook через прямой HTTP запрос

echo "🤖 Установка webhook для Telegram бота"
echo "======================================"

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "❌ Файл .env не найден. Создайте его из env.example"
    echo "   cp env.example .env"
    echo "   # Отредактируйте .env с вашими токенами"
    exit 1
fi

# Загружаем переменные из .env
export $(cat .env | grep -v '^#' | xargs)

# Проверяем обязательные переменные
if [ -z "$TELEGRAM_TOKEN" ]; then
    echo "❌ TELEGRAM_TOKEN не установлен в .env файле"
    exit 1
fi

if [ -z "$WEBHOOK_URL" ]; then
    echo "❌ WEBHOOK_URL не установлен в .env файле"
    exit 1
fi

if [ -z "$WEBHOOK_PATH" ]; then
    echo "❌ WEBHOOK_PATH не установлен в .env файле"
    exit 1
fi

# Формируем параметры
WEBHOOK_FULL_URL="${WEBHOOK_URL}${WEBHOOK_PATH}"
ALLOWED_UPDATES='["message","edited_message","business_connection","business_message","edited_business_message","deleted_business_messages"]'

echo "🔗 Webhook URL: $WEBHOOK_FULL_URL"
echo "📋 Allowed updates: $ALLOWED_UPDATES"

# Формируем URL для установки webhook
API_URL="https://api.telegram.org/bot${TELEGRAM_TOKEN}/setWebhook"

# Параметры запроса
PARAMS="url=${WEBHOOK_FULL_URL}&allowed_updates=${ALLOWED_UPDATES}"

# Добавляем secret_token если он есть
if [ ! -z "$WEBHOOK_SECRET_TOKEN" ]; then
    PARAMS="${PARAMS}&secret_token=${WEBHOOK_SECRET_TOKEN}"
    echo "🔐 Secret token: установлен"
else
    echo "⚠️  Secret token: не установлен"
fi

echo ""
echo "🚀 Устанавливаем webhook..."

# Отправляем запрос
RESPONSE=$(curl -s -X POST "${API_URL}?${PARAMS}")

# Проверяем результат
if echo "$RESPONSE" | grep -q '"ok":true'; then
    echo "✅ Webhook успешно установлен!"
    echo "📊 Ответ: $RESPONSE"
else
    echo "❌ Ошибка установки webhook"
    echo "📊 Ответ: $RESPONSE"
    exit 1
fi

echo ""
echo "🔍 Проверяем информацию о webhook..."

# Получаем информацию о webhook
INFO_RESPONSE=$(curl -s "https://api.telegram.org/bot${TELEGRAM_TOKEN}/getWebhookInfo")

if echo "$INFO_RESPONSE" | grep -q '"ok":true'; then
    echo "✅ Информация о webhook получена:"
    echo "$INFO_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$INFO_RESPONSE"
else
    echo "❌ Ошибка получения информации о webhook"
    echo "📊 Ответ: $INFO_RESPONSE"
fi

echo ""
echo "🎉 Готово! Webhook установлен и настроен."
echo "📱 Теперь бот будет получать обновления через webhook."
