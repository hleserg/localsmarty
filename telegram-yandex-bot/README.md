# Telegram Yandex Bot

Telegram-бот, использующий последнюю модель Yandex GPT для общения с пользователями через Yandex Foundation Models API.

## 📋 Описание

Этот проект представляет собой Telegram-бота, который интегрирован с Yandex Cloud и использует YandexGPT для генерации ответов на сообщения пользователей. Бот поддерживает как простые текстовые сообщения, так и команды.

## 🏗️ Структура проекта

```
telegram-yandex-bot/
├── src/
│   ├── bot.py                 # Главный файл запуска бота
│   ├── config.py             # Конфигурация проекта
│   ├── handlers/             # Обработчики команд Telegram
│   │   ├── __init__.py
│   │   └── commands.py       # Обработка команд пользователей
│   ├── services/             # Сервисы интеграции
│   │   ├── __init__.py
│   │   ├── yandex_client.py  # Клиент для Yandex Cloud API
│   │   └── telegram_client.py # Клиент для Telegram API
│   ├── utils/                # Утилиты
│   │   ├── __init__.py
│   │   └── logger.py         # Логирование
│   └── models/               # Модели данных
│       └── messages.py       # Определение моделей сообщений
├── tests/                    # Тесты
│   ├── test_bot.py          # Тесты для основного функционала
│   └── test_yandex_client.py # Тесты для Yandex Cloud интеграции
├── .env.example              # Пример файла окружения
├── requirements.txt          # Зависимости проекта
├── Dockerfile                # Docker-образ для бота
└── README.md                 # Документация проекта
```

## 🚀 Быстрый старт

### Предварительные требования

- Python 3.9+
- Аккаунт в Yandex Cloud
- Telegram Bot Token

### 1. Настройка Yandex Cloud

#### Создание сервисного аккаунта
1. Войдите в [Yandex Cloud Console](https://console.cloud.yandex.ru/)
2. Создайте новое облако или выберите существующее
3. Создайте каталог (например, `telegram-bot-folder`)
4. Перейдите в "Identity and Access Management" → "Сервисные аккаунты"
5. Нажмите "Создать сервисный аккаунт"
6. Назначьте роль `ai.languageModels.user`

#### Создание API-ключа
1. Откройте созданный сервисный аккаунт
2. На вкладке "API-ключи" нажмите "Создать API-ключ"
3. Сохраните полученный ключ

#### Получение ID каталога
1. В консоли Yandex Cloud перейдите в ваш каталог
2. Скопируйте ID каталога из URL или информации о каталоге

### 2. Создание Telegram бота

1. Найдите бота [@BotFather](https://t.me/botfather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Сохраните полученный токен

### 3. Установка и настройка

1. **Клонирование репозитория:**
   ```bash
   git clone <URL_репозитория>
   cd telegram-yandex-bot
   ```

2. **Установка зависимостей:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Настройка переменных окружения:**
   ```bash
   cp .env.example .env
   ```
   
   Отредактируйте файл `.env`:
   ```bash
   # Telegram Bot Configuration
   TELEGRAM_TOKEN=your_telegram_bot_token_here
   
   # Yandex Cloud Configuration  
   YANDEX_API_KEY=your_yandex_api_key_here
   YANDEX_FOLDER_ID=your_folder_id_here
   YANDEX_MODEL=yandexgpt-lite/latest
   
   # Logging
   LOG_LEVEL=INFO
   ```

4. **Запуск бота:**
   ```bash
   python src/bot.py
   ```

## 🐳 Docker

### Сборка и запуск

```bash
# Сборка образа
docker build -t telegram-yandex-bot .

# Запуск контейнера
docker run -d --env-file .env --name yandex-bot telegram-yandex-bot
```

## 🧪 Тестирование

Запуск всех тестов:
```bash
python -m pytest tests/ -v
```

Запуск отдельных тестов:
```bash
# Тесты Yandex Client
python -m pytest tests/test_yandex_client.py -v

# Тесты бота
python -m pytest tests/test_bot.py -v
```

## 📖 Использование

### Команды бота

- `/start` - Приветственное сообщение и краткая инструкция
- `/help` - Подробная справка о возможностях бота
- `/chat <сообщение>` - Отправка сообщения в GPT (альтернативный способ)

### Обычное использование

Просто отправьте любое текстовое сообщение боту, и он ответит с помощью YandexGPT.

### Ограничения

- Максимальная длина входящего сообщения: 4000 символов
- Максимальная длина ответа Telegram: 4096 символов (автоматически разбивается на части)
- Время ожидания ответа от API: 30 секунд

## ⚙️ Конфигурация

### Переменные окружения

| Переменная | Описание | Обязательная | По умолчанию |
|------------|----------|--------------|--------------|
| `TELEGRAM_TOKEN` | Токен Telegram бота | Да | - |
| `YANDEX_API_KEY` | API-ключ Yandex Cloud | Да | - |
| `YANDEX_FOLDER_ID` | ID каталога в Yandex Cloud | Да | - |
| `YANDEX_MODEL` | Модель YandexGPT | Нет | `yandexgpt-lite/latest` |
| `LOG_LEVEL` | Уровень логирования | Нет | `INFO` |
| `DEFAULT_TEMPERATURE` | Температура генерации | Нет | `0.7` |
| `DEFAULT_MAX_TOKENS` | Максимум токенов в ответе | Нет | `1000` |
| `REQUEST_TIMEOUT` | Таймаут запроса (сек) | Нет | `30` |

### Доступные модели YandexGPT

- `yandexgpt-lite/latest` - Быстрая модель для простых задач
- `yandexgpt/latest` - Полная модель для сложных задач

## 🐛 Решение проблем

### Частые ошибки

1. **"TELEGRAM_TOKEN environment variable is required"**
   - Убедитесь, что файл `.env` содержит корректный токен

2. **"YANDEX_API_KEY environment variable is required"**
   - Проверьте API-ключ в Yandex Cloud Console

3. **"Error: 403"** при обращении к Yandex API
   - Проверьте права сервисного аккаунта (`ai.languageModels.user`)

4. **Бот не отвечает на сообщения**
   - Проверьте логи: `tail -f combined.log`
   - Убедитесь, что бот запущен: `/start`

### Логирование

Логи сохраняются в файлы:
- `combined.log` - все логи
- `error.log` - только ошибки

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект лицензирован под MIT License - см. файл [LICENSE](LICENSE) для деталей.

## 📞 Поддержка

Для получения поддержки:
- Создайте Issue в GitHub
- Обратитесь к [документации Yandex Cloud](https://yandex.cloud/ru/docs)
- Проверьте [документацию Telegram Bot API](https://core.telegram.org/bots/api)

## 📚 Дополнительные ресурсы

- [Техническое задание проекта](../ТЗ_TELEGRAM_BOT_YANDEX_GPT.md)
- [Yandex Foundation Models API](https://yandex.cloud/ru/docs/foundation-models/)
- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)