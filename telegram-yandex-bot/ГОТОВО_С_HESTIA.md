# 🎉 ГОТОВО К РАЗВЕРТЫВАНИЮ С HESTIA НА talkbot.skhlebnikov.ru!

## ✅ Конфигурация адаптирована под ваш сервер с Hestia:

### 🌐 Ваши настройки:
- **Домен:** `talkbot.skhlebnikov.ru`
- **Порт:** `11844`
- **Webhook путь:** `/bot`
- **Полный URL:** `https://talkbot.skhlebnikov.ru/bot`
- **SSL:** Обрабатывается Hestia (не нужны сертификаты в Docker)

## 🚀 Быстрый запуск:

### 1. Настройка переменных окружения:
```bash
# Скопируйте пример и отредактируйте
cp env.example .env

# Отредактируйте .env файл с вашими токенами:
# - TELEGRAM_TOKEN=ваш_токен_бота
# - NEUROAPI_API_KEY=ваш_ключ_neuroapi
# - WEBHOOK_SECRET_TOKEN=ваш_секретный_токен
```

### 2. Запуск (SSL обрабатывается Hestia):
```bash
# Простой запуск
docker compose up -d

# Проверка
curl https://talkbot.skhlebnikov.ru/health
```

### 3. Автоматическое развертывание:
```bash
# Linux/Mac
chmod +x deploy_to_server.sh
./deploy_to_server.sh

# Windows
deploy_to_server.bat
```

## 📊 Структура развертывания с Hestia:

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

## 🔧 Обновленные файлы:

### Конфигурация:
- ✅ `src/config.py` - SSL сертификаты отключены
- ✅ `docker-compose.yml` - Nginx отключен, SSL убран
- ✅ `env.example` - SSL переменные закомментированы

### Скрипты развертывания:
- ✅ `deploy_to_server.sh` - SSL генерация убрана
- ✅ `deploy_to_server.bat` - SSL генерация убрана

### Документация:
- ✅ `HESTIA_РАЗВЕРТЫВАНИЕ.md` - инструкции для Hestia
- ✅ `РАЗВЕРТЫВАНИЕ_НА_СЕРВЕРЕ.md` - обновлено для Hestia

## 🎯 Что получилось:

1. **🌐 Webhook сервер** - готов к работе на вашем домене
2. **🔒 SSL через Hestia** - автоматическая обработка SSL
3. **📊 Мониторинг** - health checks и логи
4. **🔄 Автоматический restart** - Docker restart policy
5. **📝 Полное логирование** - все события записываются
6. **⚡ Быстрая обработка** - webhook режим
7. **🛡️ Упрощенная безопасность** - SSL через Hestia

## 📋 Проверочный список:

### Перед развертыванием:
- [ ] Настроен файл `.env` с токенами
- [ ] Docker и Docker Compose установлены
- [ ] Порт 11844 доступен
- [ ] Hestia настроен для проксирования на порт 11844

### После развертывания:
- [ ] Контейнеры запущены: `docker compose ps`
- [ ] Health check работает: `curl https://talkbot.skhlebnikov.ru/health`
- [ ] Webhook доступен: `curl https://talkbot.skhlebnikov.ru/bot`
- [ ] Логи работают: `docker compose logs -f bot`

## 🛠️ Полезные команды:

### Мониторинг:
```bash
# Статус контейнеров
docker compose ps

# Логи в реальном времени
docker compose logs -f bot

# Использование ресурсов
docker stats telegram-yandex-bot
```

### Обслуживание:
```bash
# Перезапуск бота
docker compose restart bot

# Остановка всех сервисов
docker compose down

# Обновление и перезапуск
docker compose up -d --build
```

### Проверка работы:
```bash
# Health check
curl https://talkbot.skhlebnikov.ru/health

# Проверка webhook
curl https://talkbot.skhlebnikov.ru/bot

# Проверка SSL через Hestia
openssl s_client -connect talkbot.skhlebnikov.ru:443
```

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

## 🎊 **ВСЕ ГОТОВО К РАЗВЕРТЫВАНИЮ С HESTIA!**

✅ **Конфигурация адаптирована** под ваш сервер с Hestia  
✅ **Порт 11844** настроен  
✅ **Путь /bot** настроен  
✅ **SSL через Hestia** - не нужны сертификаты в Docker  
✅ **Упрощенная конфигурация** - только бот  
✅ **Автоматические скрипты** созданы  
✅ **Документация** написана  

**Ваш бот готов к развертыванию с Hestia на talkbot.skhlebnikov.ru!** 🚀

---

## 📞 Поддержка:

Если возникли проблемы:
1. Проверьте логи: `docker compose logs -f bot`
2. Проверьте статус: `docker compose ps`
3. Проверьте порты: `netstat -tlnp | grep 11844`
4. Проверьте Hestia: `hestia list web`
5. Проверьте SSL: `openssl s_client -connect talkbot.skhlebnikov.ru:443`

**Удачного развертывания с Hestia!** ✨
