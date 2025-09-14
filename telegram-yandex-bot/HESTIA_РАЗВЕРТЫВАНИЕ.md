# 🚀 РАЗВЕРТЫВАНИЕ С HESTIA НА talkbot.skhlebnikov.ru

## ✅ Конфигурация адаптирована под ваш сервер с Hestia:

### 🌐 Ваши настройки:
- **Домен:** `talkbot.skhlebnikov.ru`
- **Порт:** `11844`
- **Webhook путь:** `/bot`
- **Полный URL:** `https://talkbot.skhlebnikov.ru/bot`
- **SSL:** Обрабатывается Hestia (не нужны сертификаты в Docker)

## 🔧 Настройка для вашего сервера с Hestia:

### 1. Создайте файл `.env`:
```bash
# Telegram Bot Configuration
TELEGRAM_TOKEN=your_telegram_bot_token_here

# NeuroAPI Configuration
NEUROAPI_API_KEY=your_neuroapi_api_key_here
NEUROAPI_TEMPERATURE=0.7
NEUROAPI_MAX_TOKENS=1000

# Bot Configuration
ENABLE_CONTEXT=true
LOG_LEVEL=INFO

# Webhook Configuration для talkbot.skhlebnikov.ru
WEBHOOK_URL=https://talkbot.skhlebnikov.ru
WEBHOOK_PORT=11844
WEBHOOK_HOST=0.0.0.0
WEBHOOK_PATH=/bot
# SSL сертификаты не нужны - обрабатываются Hestia
WEBHOOK_SECRET_TOKEN=your_secret_token_here

# Voice Configuration
ENABLE_VOICE=false
STT_LANGUAGE=ru-RU
TTS_VOICE=alena
TTS_FORMAT=oggopus
AUDIO_MAX_DURATION_SEC=60
ENABLE_TTS_REPLY=false
```

### 2. Запуск на сервере:

#### Простой запуск (только бот):
```bash
docker compose up -d
```

#### С Nginx (если нужен дополнительный прокси):
```bash
docker compose --profile nginx up -d
```

### 3. Проверка работы:

#### Health check:
```bash
curl https://talkbot.skhlebnikov.ru/health
```

#### Проверка webhook:
```bash
curl https://talkbot.skhlebnikov.ru/bot
```

#### Логи:
```bash
docker compose logs -f bot
```

## 🔍 Структура развертывания с Hestia:

### Docker Compose сервисы:
- ✅ **bot** - webhook сервер на порту 11844
- ❌ **nginx** - отключен (у вас уже есть Hestia)

### Порты:
- ✅ **11844** - webhook сервер (ваш порт)
- ❌ **80** - не нужен (обрабатывается Hestia)
- ❌ **443** - не нужен (обрабатывается Hestia)

### Endpoints:
- ✅ **`/bot`** - webhook endpoint (ваш путь)
- ✅ **`/health`** - health check
- ✅ **`/`** - статус сервера

## 📊 Мониторинг:

### Проверка статуса контейнеров:
```bash
docker compose ps
```

### Логи в реальном времени:
```bash
docker compose logs -f bot
```

### Использование ресурсов:
```bash
docker stats telegram-yandex-bot
```

### Перезапуск сервиса:
```bash
docker compose restart bot
```

## 🛠️ Обслуживание:

### Обновление бота:
```bash
# Остановка
docker compose down

# Обновление кода
git pull

# Пересборка и запуск
docker compose up -d --build
```

### Резервное копирование логов:
```bash
# Создание архива логов
tar -czf logs_backup_$(date +%Y%m%d_%H%M%S).tar.gz logs/

# Копирование на другой сервер
scp logs_backup_*.tar.gz user@backup-server:/backups/
```

### Очистка старых логов:
```bash
# Очистка логов старше 30 дней
find logs/ -name "*.log" -mtime +30 -delete
```

## 🔒 Безопасность с Hestia:

### Firewall настройки:
```bash
# Разрешить только необходимые порты
ufw allow 11844/tcp
ufw deny 80/tcp    # Обрабатывается Hestia
ufw deny 443/tcp   # Обрабатывается Hestia
```

### SSL сертификаты:
- ✅ Обрабатываются Hestia автоматически
- ✅ Let's Encrypt интеграция
- ✅ Автоматическое обновление

## 🎯 Преимущества конфигурации с Hestia:

1. **🌐 Публичный домен** - `talkbot.skhlebnikov.ru`
2. **🔒 SSL защита** - автоматически через Hestia
3. **📊 Мониторинг** - health checks
4. **🔄 Автоматический restart** - Docker restart policy
5. **📝 Полное логирование** - все события записываются
6. **⚡ Быстрая обработка** - webhook режим
7. **🛡️ Упрощенная безопасность** - SSL через Hestia

## 🚀 Команды для быстрого запуска:

```bash
# 1. Клонирование и настройка
git clone <your-repo>
cd telegram-yandex-bot

# 2. Настройка переменных
cp env.example .env
# Отредактируйте .env с вашими токенами

# 3. Запуск (SSL обрабатывается Hestia)
docker compose up -d

# 4. Проверка
curl https://talkbot.skhlebnikov.ru/health
```

## 📞 Поддержка:

Если возникли проблемы:
1. Проверьте логи: `docker compose logs -f bot`
2. Проверьте статус: `docker compose ps`
3. Проверьте порты: `netstat -tlnp | grep 11844`
4. Проверьте Hestia: `hestia list web`
5. Проверьте SSL: `openssl s_client -connect talkbot.skhlebnikov.ru:443`

## 🔧 Настройка Hestia:

### Проверка конфигурации Hestia:
```bash
# Список веб-сайтов
hestia list web

# Проверка конфигурации Nginx
hestia list web-domain talkbot.skhlebnikov.ru

# Проверка SSL
hestia list web-domain-ssl talkbot.skhlebnikov.ru
```

### Обновление конфигурации Hestia:
```bash
# Перезапуск Nginx
hestia restart web

# Проверка статуса
hestia status web
```

**Ваш бот готов к работе с Hestia на сервере talkbot.skhlebnikov.ru!** 🎉

---

## 🎊 **ВСЕ ГОТОВО К РАЗВЕРТЫВАНИЮ С HESTIA!**

✅ **Конфигурация адаптирована** под ваш сервер с Hestia  
✅ **Порт 11844** настроен  
✅ **Путь /bot** настроен  
✅ **SSL через Hestia** - не нужны сертификаты в Docker  
✅ **Упрощенная конфигурация** - только бот  
✅ **Автоматические скрипты** созданы  
✅ **Документация** написана  

**Просто запустите `docker compose up -d` и ваш бот будет работать!** 🚀
