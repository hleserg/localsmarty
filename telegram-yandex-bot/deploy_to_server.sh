#!/bin/bash

# Скрипт для развертывания бота на сервере talkbot.skhlebnikov.ru

echo "🚀 Развертывание Telegram Bot на talkbot.skhlebnikov.ru"
echo "======================================================"

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Установите Docker и попробуйте снова."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен. Установите Docker Compose и попробуйте снова."
    exit 1
fi

echo "✅ Docker и Docker Compose найдены"

# Создаем .env если его нет
if [ ! -f .env ]; then
    echo "📝 Создаем файл .env из примера..."
    cp env.example .env
    echo "⚠️  ВНИМАНИЕ: Отредактируйте файл .env с вашими токенами!"
    echo "   - TELEGRAM_TOKEN"
    echo "   - NEUROAPI_API_KEY"
    echo "   - WEBHOOK_SECRET_TOKEN"
    echo ""
    read -p "Нажмите Enter после редактирования .env файла..."
fi

# SSL сертификаты не нужны - обрабатываются Hestia
echo "✅ SSL сертификаты обрабатываются Hestia - генерация не нужна"

# Создаем директории
echo "📁 Создаем необходимые директории..."
mkdir -p logs

# Останавливаем старые контейнеры
echo "🛑 Останавливаем старые контейнеры..."
docker compose down

# Собираем и запускаем новые контейнеры
echo "🔨 Собираем и запускаем контейнеры..."
docker compose up -d --build

# Ждем запуска
echo "⏳ Ждем запуска сервисов..."
sleep 10

# Проверяем статус
echo "📊 Проверяем статус сервисов..."
docker compose ps

# Проверяем health check
echo "❤️ Проверяем health check..."
if curl -f http://localhost:11844/health > /dev/null 2>&1; then
    echo "✅ Health check прошел успешно"
else
    echo "❌ Health check не прошел. Проверьте логи:"
    echo "   docker compose logs -f bot"
fi

echo ""
echo "🎉 Развертывание завершено!"
echo ""
echo "📋 Информация о развертывании:"
echo "   🌐 Домен: talkbot.skhlebnikov.ru"
echo "   🔗 Webhook URL: https://talkbot.skhlebnikov.ru/bot"
echo "   🔌 Порт: 11844"
echo "   ❤️ Health check: https://talkbot.skhlebnikov.ru/health"
echo ""
echo "📝 Полезные команды:"
echo "   Логи: docker compose logs -f bot"
echo "   Статус: docker compose ps"
echo "   Перезапуск: docker compose restart bot"
echo "   Остановка: docker compose down"
echo ""
echo "🔍 Проверьте работу бота, отправив сообщение в Telegram!"
