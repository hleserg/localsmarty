# Техническое задание (ТЗ): Telegram Bot с интеграцией Yandex Cloud GPT

## 1. Общее описание проекта

### 1.1 Цель проекта
Разработка простого Telegram-бота, который обеспечивает общение пользователей с последней моделью Yandex GPT через Yandex Cloud.

### 1.2 Основные задачи
- Создание Telegram-бота на языке Python
- Интеграция с Yandex Foundation Models API (YandexGPT)
- Обеспечение надежной обработки сообщений пользователей
- Реализация логирования и обработки ошибок
- Возможность развертывания в Docker-контейнере

### 1.3 Целевая аудитория
Конечные пользователи Telegram, желающие взаимодействовать с возможностями искусственного интеллекта Yandex GPT.

## 2. Техническая архитектура

### 2.1 Технологический стек
- **Язык программирования**: Python 3.9+
- **Основные библиотеки**: 
  - `python-telegram-bot` - для работы с Telegram Bot API
  - `requests` - для HTTP-запросов к Yandex Cloud API
  - `python-dotenv` - для управления переменными окружения
  - `pydantic` - для валидации данных
- **Облачная платформа**: Yandex Cloud
- **AI модель**: Yandex Foundation Models (YandexGPT)

### 2.2 Архитектура приложения
```
telegram-yandex-bot/
├── src/
│   ├── bot.py                 # Главный файл запуска бота
│   ├── config.py             # Конфигурация проекта
│   ├── handlers/             # Обработчики команд Telegram
│   │   ├── __init__.py
│   │   └── commands.py
│   ├── services/             # Сервисы интеграции
│   │   ├── __init__.py
│   │   ├── yandex_client.py  # Клиент для Yandex Cloud API
│   │   └── telegram_client.py
│   ├── utils/                # Утилиты
│   │   ├── __init__.py
│   │   └── logger.py
│   └── models/               # Модели данных
│       └── messages.py
├── tests/                    # Тесты
├── .env.example             # Пример переменных окружения
├── requirements.txt         # Зависимости
├── Dockerfile              # Docker-образ
└── README.md               # Документация
```

## 3. Интеграция с Yandex Cloud

### 3.1 Настройка Yandex Cloud Console

#### Шаг 1: Создание облака и каталога
1. Войдите в [Yandex Cloud Console](https://console.cloud.yandex.ru/)
2. Создайте новое облако или выберите существующее
3. Создайте каталог для проекта (например, `telegram-bot-folder`)

#### Шаг 2: Создание сервисного аккаунта
1. Перейдите в раздел "Identity and Access Management" → "Сервисные аккаунты"
2. Нажмите "Создать сервисный аккаунт"
3. Укажите имя: `telegram-bot-service-account`
4. Назначьте роли:
   - `ai.languageModels.user` - для использования Foundation Models
   - `editor` - для управления ресурсами (опционально)

#### Шаг 3: Создание API-ключа
1. Откройте созданный сервисный аккаунт
2. На вкладке "API-ключи" нажмите "Создать API-ключ"
3. Сохраните полученный API-ключ в безопасном месте

#### Шаг 4: Получение ID каталога
1. В консоли Yandex Cloud перейдите в ваш каталог
2. Скопируйте ID каталога из URL или информации о каталоге

### 3.2 Yandex Foundation Models API

#### 3.2.1 Endpoint и аутентификация
- **API Endpoint**: `https://llm.api.cloud.yandex.net/foundationModels/v1/completion`
- **Метод аутентификации**: API-ключ в заголовке `Authorization: Api-Key <your-api-key>`
- **Модель**: `yandexgpt-lite/latest` (для быстрых ответов) или `yandexgpt/latest` (для более качественных ответов)

#### 3.2.2 Формат запроса
```json
{
  "modelUri": "gpt://<folder-id>/yandexgpt-lite/latest",
  "completionOptions": {
    "stream": false,
    "temperature": 0.7,
    "maxTokens": 1000
  },
  "messages": [
    {
      "role": "user",
      "text": "Текст сообщения пользователя"
    }
  ]
}
```

#### 3.2.3 Формат ответа
```json
{
  "result": {
    "alternatives": [
      {
        "message": {
          "role": "assistant",
          "text": "Ответ от YandexGPT"
        },
        "status": "ALTERNATIVE_STATUS_FINAL"
      }
    ],
    "usage": {
      "inputTextTokens": "50",
      "completionTokens": "100",
      "totalTokens": "150"
    },
    "modelVersion": "06.12.2023"
  }
}
```

## 4. Настройка переменных окружения

### 4.1 Файл .env
Создайте файл `.env` на основе `.env.example`:

```bash
# Telegram Bot Configuration
TELEGRAM_TOKEN=<your-telegram-bot-token>

# Yandex Cloud Configuration  
YANDEX_API_KEY=<your-yandex-api-key>
YANDEX_FOLDER_ID=<your-folder-id>
YANDEX_MODEL=yandexgpt-lite/latest

# Logging
LOG_LEVEL=INFO
```

### 4.2 Получение Telegram Bot Token
1. Найдите бота [@BotFather](https://t.me/botfather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Получите и сохраните токен бота

## 5. Функциональные требования

### 5.1 Основной функционал
- **Команда /start**: Приветственное сообщение и краткая инструкция
- **Команда /help**: Список доступных команд и их описание
- **Обработка текстовых сообщений**: Отправка сообщений в YandexGPT и возврат ответа
- **Обработка ошибок**: Корректная обработка ошибок API и сетевых проблем

### 5.2 Дополнительный функционал
- **Логирование**: Запись всех операций и ошибок
- **Ограничение длины сообщений**: Контроль размера входящих сообщений
- **Таймауты**: Установка разумных таймаутов для API-запросов

## 6. Нефункциональные требования

### 6.1 Производительность
- Время ответа бота: не более 10 секунд
- Обработка до 100 запросов в минуту
- Graceful handling при недоступности API

### 6.2 Надежность
- Автоматическое восстановление соединения
- Retry-логика для failed запросов
- Comprehensive error handling

### 6.3 Безопасность
- Валидация входных данных
- Безопасное хранение API-ключей
- Логирование без sensitive данных

## 7. Развертывание

### 7.1 Локальное развертывание
```bash
# Клонирование репозитория
git clone <repository-url>
cd telegram-yandex-bot

# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных окружения
cp .env.example .env
# Отредактируйте .env с вашими ключами

# Запуск бота
python src/bot.py
```

### 7.2 Docker развертывание
```bash
# Сборка образа
docker build -t telegram-yandex-bot .

# Запуск контейнера
docker run -d --env-file .env telegram-yandex-bot
```

### 7.3 Yandex Cloud развертывание
Возможные варианты:
- **Yandex Cloud Functions** - serverless развертывание
- **Yandex Compute Cloud** - на виртуальной машине
- **Yandex Container Registry** + **Yandex Managed Service for Kubernetes**

## 8. Тестирование

### 8.1 Unit тесты
- Тестирование YandexClient
- Тестирование обработчиков команд
- Тестирование парсинга конфигурации

### 8.2 Integration тесты
- Тестирование интеграции с Telegram API
- Тестирование интеграции с Yandex Cloud API
- End-to-end тестирование функциональности бота

### 8.3 Запуск тестов
```bash
python -m pytest tests/
```

## 9. Мониторинг и логирование

### 9.1 Логирование
- Структурированные логи в формате JSON
- Различные уровни логирования (DEBUG, INFO, WARNING, ERROR)
- Ротация логов по размеру/времени

### 9.2 Мониторинг
- Мониторинг использования API Yandex Cloud
- Мониторинг ошибок и производительности
- Уведомления о критических ошибках

## 10. Ограничения и лимиты

### 10.1 Yandex Cloud лимиты
- Лимиты на количество запросов в минуту/час
- Лимиты на размер входящих/исходящих сообщений
- Стоимость использования API

### 10.2 Telegram лимиты
- Лимит на количество сообщений в секунду
- Максимальная длина сообщения: 4096 символов

## 11. Дальнейшее развитие

### 11.1 Возможные улучшения
- Добавление контекста беседы (memory)
- Поддержка различных моделей YandexGPT
- Добавление команд для настройки параметров модели
- Интеграция с базой данных для хранения истории
- Добавление rate limiting на пользователя
- Веб-интерфейс для администрирования

### 11.2 Масштабирование
- Горизонтальное масштабирование через load balancer
- Использование очередей сообщений (например, Yandex Message Queue)
- Кеширование часто используемых ответов

## 12. Контакты и поддержка

При возникновении вопросов по реализации обращайтесь к:
- Официальной документации Yandex Cloud
- Сообществу разработчиков Telegram Bot API
- GitHub Issues проекта