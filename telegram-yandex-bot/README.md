# Telegram Yandex Bot

Этот проект представляет собой Telegram-бота, который использует актуальную модель YandexGPT через Foundation Models API для общения с пользователями. Бот подключен к Yandex Cloud и поддерживает как текстовые, так и голосовые сообщения.

## Возможности

- 🤖 **Интеграция с YandexGPT**: Использует актуальный Foundation Models API
- 🗣️ **Голосовые сообщения**: Поддержка STT и TTS через SpeechKit
- 🧠 **Контекст диалога**: Запоминает последние сообщения в рамках чата
- 📱 **Команды**: /start, /help, /ping
- 🔧 **Конфигурируемость**: Все настройки через переменные окружения
- ⚡ **Современная архитектура**: python-telegram-bot v20.7, типизация, error handling

## Структура проекта

```
telegram-yandex-bot
├── src
│   ├── bot.py                  # Точка входа для бота
│   ├── config.py               # Конфигурационные параметры
│   ├── handlers                # Пакет обработчиков
│   │   ├── __init__.py
│   │   ├── commands.py         # Обработка команд (/start, /help, /ping)
│   │   └── voice.py            # Обработка голосовых сообщений
│   └── services                # Пакет сервисов
│       ├── __init__.py
│       ├── yandex_client.py    # Взаимодействие с YandexGPT
│       └── speech_client.py    # Взаимодействие с SpeechKit
├── tests                       # Тесты
│   ├── test_bot.py            # Тесты основного функционала
│   ├── test_yandex_client.py  # Тесты YandexGPT клиента
│   └── test_speech_client.py  # Тесты SpeechKit клиента
├── docs
│   └── TZ_yandex_gpt_telegram_bot.md  # Техническое задание
├── .env.example               # Пример файла окружения
├── .gitignore                 # Исключения для git
├── requirements.txt           # Зависимости проекта
├── Dockerfile                 # Docker-образ для бота
└── README.md                  # Документация проекта
```

## Установка

### Локальная установка

1. Клонируйте репозиторий:
   ```bash
   git clone <URL_репозитория>
   cd telegram-yandex-bot
   ```

2. Создайте виртуальное окружение:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # или
   .venv\Scripts\activate     # Windows
   ```

3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

4. Настройте файл окружения:
   ```bash
   cp .env.example .env
   # Отредактируйте .env файл с вашими данными
   ```

### Настройка Yandex Cloud

1. Создайте каталог в Yandex Cloud и сохраните `FOLDER_ID`
2. Создайте сервисный аккаунт с ролями:
   - `ai.languageModels.user` (для YandexGPT)
   - Роли для SpeechKit (при использовании голосовых функций)
3. Получите API-ключ или IAM-токен для сервисного аккаунта

Подробная инструкция в [техническом задании](docs/TZ_yandex_gpt_telegram_bot.md).

## Конфигурация

Основные переменные окружения в `.env`:

```bash
# Обязательные
TELEGRAM_TOKEN=your_telegram_bot_token
YC_FOLDER_ID=your_yandex_cloud_folder_id
YC_API_KEY=your_yandex_api_key

# Опциональные
YC_MODEL_URI=gpt://your_folder_id/yandexgpt/latest
YC_TEMPERATURE=0.3
YC_MAX_TOKENS=800
ENABLE_CONTEXT=true
ENABLE_VOICE=false
LOG_LEVEL=INFO
```

## Запуск

### Локальный запуск
```bash
python src/bot.py
```

### Запуск с Docker
```bash
docker build -t telegram-yandex-bot .
docker run -d --env-file .env telegram-yandex-bot
```

## Тестирование

Запуск всех тестов:
```bash
python -m unittest discover tests -v
```

Запуск конкретного теста:
```bash
python -m unittest tests.test_yandex_client -v
```

## Использование

### Текстовые команды
- `/start` - Начать работу с ботом
- `/help` - Получить справку
- `/ping` - Проверить работоспособность

### Сообщения
Просто отправьте текстовое сообщение боту - он ответит с помощью YandexGPT.

### Голосовые сообщения (при включении)
Отправьте голосовое сообщение - бот распознает речь и ответит текстом.

## Разработка

Код следует принципам:
- Типизация с type hints
- Обработка ошибок
- Логирование
- Модульная архитектура
- Тестирование

## Лицензия

Этот проект лицензирован под MIT License.