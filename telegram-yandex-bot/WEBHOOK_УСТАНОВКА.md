# 🔗 УСТАНОВКА WEBHOOK ДЛЯ TELEGRAM БОТА

## ✅ Webhook настроен с новыми параметрами:

### 🌐 Конфигурация:
- **URL:** `https://talkbot.skhlebnikov.ru/bot`
- **Allowed Updates:** `["message","edited_message","business_connection","business_message","edited_business_message","deleted_business_messages"]`
- **Secret Token:** Настроен (если указан в .env)
- **SSL:** Обрабатывается Hestia

## 🚀 Способы установки webhook:

### 1. Автоматическая установка (в коде бота):
```python
# В src/bot.py - функция setup_webhook()
allowed_updates = [
    "message",
    "edited_message", 
    "business_connection",
    "business_message",
    "edited_business_message",
    "deleted_business_messages"
]

await application.bot.set_webhook(
    url=webhook_url,
    allowed_updates=allowed_updates,
    secret_token=config.WEBHOOK_SECRET_TOKEN
)
```

### 2. Ручная установка через скрипт:
```bash
# Linux/Mac
python set_webhook.py set

# Windows
python set_webhook.py set
```

### 3. Прямой HTTP запрос:
```bash
curl -X POST "https://api.telegram.org/botTOKEN/setWebhook" \
  -d "url=https://talkbot.skhlebnikov.ru/bot" \
  -d "allowed_updates=[\"message\",\"edited_message\",\"business_connection\",\"business_message\",\"edited_business_message\",\"deleted_business_messages\"]" \
  -d "secret_token=YOUR_SECRET_TOKEN"
```

### 4. PowerShell (Windows):
```powershell
$params = @{
    url = "https://talkbot.skhlebnikov.ru/bot"
    allowed_updates = '["message","edited_message","business_connection","business_message","edited_business_message","deleted_business_messages"]'
    secret_token = "YOUR_SECRET_TOKEN"
}

Invoke-RestMethod -Uri "https://api.telegram.org/botTOKEN/setWebhook" -Method Post -Body $params
```

## 🔧 Управление webhook:

### Проверка статуса:
```bash
# Через скрипт
python set_webhook.py info

# Прямой запрос
curl "https://api.telegram.org/botTOKEN/getWebhookInfo"
```

### Удаление webhook:
```bash
# Через скрипт
python set_webhook.py delete

# Прямой запрос
curl -X POST "https://api.telegram.org/botTOKEN/deleteWebhook"
```

### Переустановка webhook:
```bash
# Через скрипт
python set_webhook.py delete
python set_webhook.py set

# Или автоматически при запуске бота
docker compose up -d --build
```

## 📊 Allowed Updates объяснение:

### Основные типы:
- **`message`** - обычные сообщения
- **`edited_message`** - отредактированные сообщения

### Business функции:
- **`business_connection`** - подключение к бизнес-аккаунту
- **`business_message`** - сообщения в бизнес-чате
- **`edited_business_message`** - отредактированные бизнес-сообщения
- **`deleted_business_messages`** - удаленные бизнес-сообщения

### Другие типы (не включены):
- `channel_post` - сообщения в каналах
- `edited_channel_post` - отредактированные сообщения в каналах
- `inline_query` - inline запросы
- `chosen_inline_result` - выбранные inline результаты
- `callback_query` - callback кнопки
- `shipping_query` - запросы доставки
- `pre_checkout_query` - предварительные запросы оплаты
- `poll` - опросы
- `poll_answer` - ответы на опросы
- `my_chat_member` - изменения статуса бота в чате
- `chat_member` - изменения статуса участников чата
- `chat_join_request` - запросы на вступление в чат

## 🔍 Проверка работы:

### 1. Проверка webhook:
```bash
curl "https://api.telegram.org/botTOKEN/getWebhookInfo"
```

### 2. Проверка health check:
```bash
curl https://talkbot.skhlebnikov.ru/health
```

### 3. Проверка статуса бота:
```bash
curl https://talkbot.skhlebnikov.ru/
```

### 4. Проверка логов:
```bash
docker compose logs -f bot
```

## 🛠️ Скрипты для управления:

### `set_webhook.py` - Python скрипт:
```bash
python set_webhook.py set      # Установить webhook
python set_webhook.py delete   # Удалить webhook
python set_webhook.py info     # Показать информацию
```

### `install_webhook.sh` - Bash скрипт:
```bash
chmod +x install_webhook.sh
./install_webhook.sh
```

### `install_webhook.bat` - Windows скрипт:
```cmd
install_webhook.bat
```

## 📋 Требования:

### Переменные окружения (.env):
```env
TELEGRAM_TOKEN=your_bot_token
WEBHOOK_URL=https://talkbot.skhlebnikov.ru
WEBHOOK_PATH=/bot
WEBHOOK_SECRET_TOKEN=your_secret_token
```

### Зависимости:
- `requests` - для HTTP запросов
- `python-dotenv` - для загрузки .env

## 🎯 Результат:

✅ **Webhook установлен** с правильными allowed_updates  
✅ **Бот готов** к получению обновлений  
✅ **SSL обрабатывается** Hestia  
✅ **Мониторинг работает** через health check  
✅ **Логирование включено** для всех событий  

**Ваш бот готов к работе с обновленным webhook!** 🚀
