# 💼 ОБРАБОТКА BUSINESS MESSAGE

## ✅ Добавлена поддержка business_message обновлений:

### 🌐 Что обрабатывается:
- **business_message** - сообщения в бизнес-чатах
- **edited_business_message** - отредактированные бизнес-сообщения
- **deleted_business_messages** - удаленные бизнес-сообщения
- **business_connection** - подключение к бизнес-аккаунту

## 🔧 Реализация:

### 1. Обработчик business_message:
```python
async def handle_business_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for business messages"""
    if not update.business_message or not update.effective_chat or not update.effective_user:
        return
    
    user_message = update.business_message.text or ""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    username = update.effective_user.username
    message_id = update.business_message.message_id
    business_connection_id = update.business_message.business_connection_id

    # Логируем входящее бизнес-сообщение
    log_message(
        chat_id=chat_id,
        user_id=user_id,
        username=username,
        message_type="BUSINESS_MESSAGE",
        content=user_message,
        message_id=message_id
    )

    try:
        # Get response from NeuroAPI GPT-5
        gpt_response = get_gpt_response(user_message, chat_id)
        
        # Отправляем ответ в бизнес-чат
        await update.business_message.reply_text(
            gpt_response,
            disable_web_page_preview=True
        )
        
        log_response(chat_id, "BUSINESS_MESSAGE", True)
    except Exception as e:
        logger.error(f"Error handling business message for chat {chat_id}: {str(e)}")
        log_response(chat_id, "BUSINESS_MESSAGE", False, str(e))
        
        try:
            await update.business_message.reply_text(
                "Извините, произошла ошибка при обработке вашего сообщения. Попробуйте позже.",
                disable_web_page_preview=True
            )
        except Exception as reply_error:
            logger.error(f"Error sending error reply for business message: {reply_error}")
```

### 2. Webhook обработчик:
```python
async def webhook_handler(request):
    """Обработчик webhook запросов"""
    try:
        # Получаем данные из запроса
        data = await request.json()
        
        # Создаем Update объект
        update = Update.de_json(data, None)
        
        # Проверяем, является ли это business_message
        if update.business_message:
            await handle_business_message_update(update)
        else:
            # Обрабатываем обычный update
            await application.process_update(update)
        
        return web.Response(text="OK")
        
    except Exception as e:
        log_error(f"Error processing webhook: {e}")
        return web.Response(text="Error", status=500)
```

## 📊 Структура business_message:

### Пример входящего обновления:
```json
{
  "timestamp": "2025-09-14 03:17:39",
  "update": {
    "business_message": {
      "business_connection_id": "o1z9umxS4UmeDwAAMz5UekAA75o",
      "channel_chat_created": false,
      "delete_chat_photo": false,
      "group_chat_created": false,
      "supergroup_chat_created": false,
      "text": "Привет сережа",
      "chat": {
        "first_name": "Сергей",
        "id": 1111576171,
        "last_name": "Хлебников",
        "type": "private"
      },
      "date": 1757819859,
      "message_id": 374709,
      "from": {
        "first_name": "Сергей",
        "id": 1111576171,
        "is_bot": false,
        "language_code": "ru",
        "last_name": "Хлебников"
      }
    },
    "update_id": 240051469
  }
}
```

### Поля business_message:
- **`business_connection_id`** - ID бизнес-подключения
- **`text`** - текст сообщения
- **`chat`** - информация о чате
- **`from`** - информация об отправителе
- **`message_id`** - ID сообщения
- **`date`** - дата отправки

## 🔍 Логирование:

### Типы логов:
- **`BUSINESS_MESSAGE`** - входящие бизнес-сообщения
- **`BUSINESS_MESSAGE`** - ответы на бизнес-сообщения

### Пример лога:
```
[2025-09-14 03:17:39] CHAT:1111576171 USER:1111576171 (Сергей) TYPE:BUSINESS_MESSAGE ID:374709 CONTENT:Привет сережа
[2025-09-14 03:17:40] CHAT:1111576171 RESPONSE:BUSINESS_MESSAGE STATUS:SUCCESS
```

## 🚀 Как это работает:

### 1. Получение обновления:
- Telegram отправляет webhook с business_message
- Бот получает обновление через `/bot` endpoint
- Проверяется тип обновления

### 2. Обработка:
- Извлекается текст сообщения
- Логируется входящее сообщение
- Отправляется запрос к NeuroAPI GPT-5
- Получается ответ от GPT-5

### 3. Ответ:
- Отправляется ответ в бизнес-чат
- Логируется успешный ответ
- При ошибке отправляется сообщение об ошибке

## 🛠️ Настройка:

### Webhook allowed_updates:
```json
[
  "message",
  "edited_message",
  "business_connection",
  "business_message",
  "edited_business_message",
  "deleted_business_messages"
]
```

### Переменные окружения:
```env
TELEGRAM_TOKEN=your_bot_token
WEBHOOK_URL=https://talkbot.skhlebnikov.ru
WEBHOOK_PATH=/bot
NEUROAPI_API_KEY=your_neuroapi_key
```

## 📋 Проверка работы:

### 1. Проверка webhook:
```bash
python set_webhook.py info
```

### 2. Проверка логов:
```bash
docker compose logs -f bot
```

### 3. Тестирование:
- Отправьте сообщение в бизнес-чат
- Проверьте логи на наличие `BUSINESS_MESSAGE`
- Убедитесь, что бот отвечает через NeuroAPI

## 🎯 Результат:

✅ **Business message поддержка** добавлена  
✅ **NeuroAPI интеграция** работает  
✅ **Логирование** включено  
✅ **Обработка ошибок** реализована  
✅ **Webhook** настроен правильно  

**Теперь бот отвечает на business_message через NeuroAPI GPT-5!** 🚀
