# Тесты для Telegram бота

Этот каталог содержит комплексное тестовое покрытие для Telegram бота с интеграцией GPT-5 через NeuroAPI.

## Структура тестов

### Основные тесты
- `test_config.py` - Тесты конфигурации
- `test_models.py` - Тесты моделей данных
- `test_utils_markdown.py` - Тесты утилит Markdown
- `test_utils_logger.py` - Тесты утилит логирования

### Тесты сервисов
- `test_services_neuroapi.py` - Тесты NeuroAPI клиента
- `test_services_speech_enhanced.py` - Расширенные тесты Speech клиента
- `test_services_yandex_enhanced.py` - Расширенные тесты Yandex клиента
- `test_services_iam_token_manager.py` - Тесты IAM Token Manager
- `test_services_telegram_client.py` - Тесты Telegram клиента

### Тесты обработчиков
- `test_handlers_commands.py` - Тесты обработчиков команд
- `test_handlers_voice.py` - Тесты обработчиков голосовых сообщений

### Интеграционные тесты
- `test_integration.py` - Интеграционные тесты
- `test_bot_enhanced.py` - Расширенные тесты основного модуля бота

### Специальные тесты
- `test_performance.py` - Тесты производительности
- `test_error_handling.py` - Тесты обработки ошибок
- `test_webhook_skip.py` - Тесты webhook (пропускаются локально)
- `test_webhook_local_skip.py` - Дополнительные тесты пропуска webhook

## Установка зависимостей

```bash
pip install pytest pytest-asyncio pytest-mock
```

## Запуск тестов

### Запуск всех тестов
```bash
pytest
```

### Запуск тестов по категориям
```bash
# Только unit тесты
pytest -m unit

# Только интеграционные тесты
pytest -m integration

# Только тесты сервисов
pytest -m services

# Только тесты обработчиков
pytest -m handlers

# Только тесты утилит
pytest -m utils

# Только тесты конфигурации
pytest -m config

# Только тесты моделей
pytest -m models
```

### Запуск тестов с подробным выводом
```bash
pytest -v
```

### Запуск тестов с покрытием кода
```bash
pytest --cov=src
```

### Запуск медленных тестов
```bash
pytest -m slow
```

## Особенности webhook тестов

Webhook тесты автоматически пропускаются при локальном запуске, так как webhook работает только на выделенном сервере. Это реализовано через:

1. **Маркеры pytest** - тесты с маркером `@pytest.mark.webhook` пропускаются локально
2. **Автоматическая проверка** в `conftest.py` - определяет локальную среду по переменным окружения
3. **Условные пропуски** - различные способы пропуска тестов в зависимости от окружения

### Переменные окружения для webhook тестов
- `WEBHOOK_URL` - URL webhook (должен быть HTTPS и не localhost)
- `WEBHOOK_PORT` - порт webhook
- `WEBHOOK_PATH` - путь webhook
- `WEBHOOK_SECRET_TOKEN` - секретный токен webhook

## Конфигурация тестов

### pytest.ini
Основная конфигурация pytest с маркерами и настройками.

### conftest.py
Содержит фикстуры и автоматическую настройку тестовой среды:
- Моки для Telegram объектов
- Тестовая конфигурация
- Временные директории
- Моки HTTP ответов

## Фикстуры

### Основные фикстуры
- `mock_config` - мок конфигурации
- `mock_user` - мок пользователя Telegram
- `mock_chat` - мок чата Telegram
- `mock_message` - мок сообщения
- `mock_update` - мок Update объекта
- `mock_context` - мок контекста обработчика

### Специальные фикстуры
- `temp_log_dir` - временная директория для логов
- `sample_context_data` - пример данных контекста
- `mock_neuroapi_response` - мок ответа NeuroAPI
- `mock_speech_response` - мок ответа Speech API
- `mock_yandex_response` - мок ответа Yandex GPT

## Маркеры тестов

- `@pytest.mark.unit` - unit тесты
- `@pytest.mark.integration` - интеграционные тесты
- `@pytest.mark.services` - тесты сервисов
- `@pytest.mark.handlers` - тесты обработчиков
- `@pytest.mark.utils` - тесты утилит
- `@pytest.mark.config` - тесты конфигурации
- `@pytest.mark.models` - тесты моделей
- `@pytest.mark.webhook` - тесты webhook (пропускаются локально)
- `@pytest.mark.slow` - медленные тесты
- `@pytest.mark.mock` - тесты с моками

## Примеры использования

### Тест с моками
```python
@pytest.mark.services
def test_neuroapi_client(mock_config, mock_neuroapi_response):
    with patch('services.neuroapi_client.requests.post') as mock_post:
        mock_post.return_value = mock_neuroapi_response
        client = NeuroAPIClient()
        response = client.get_response("Тест", 12345)
        assert response == "Тестовый ответ"
```

### Асинхронный тест
```python
@pytest.mark.asyncio
async def test_command_handler(mock_update, mock_context):
    await handle_text_message(mock_update, mock_context)
    # Проверки...
```

### Тест с пропуском webhook
```python
@pytest.mark.webhook
def test_webhook_functionality():
    # Этот тест будет пропущен локально
    pytest.skip("Webhook tests only work on dedicated server")
```

## Отладка тестов

### Запуск конкретного теста
```bash
pytest tests/test_config.py::TestConfig::test_config_initialization
```

### Запуск с отладочным выводом
```bash
pytest -s -v
```

### Запуск с остановкой на первой ошибке
```bash
pytest -x
```

## Покрытие кода

Для измерения покрытия кода установите pytest-cov:
```bash
pip install pytest-cov
```

Запуск с покрытием:
```bash
pytest --cov=src --cov-report=html
```

Отчет будет создан в `htmlcov/index.html`.

## Непрерывная интеграция

Тесты настроены для работы в CI/CD:
- Автоматический пропуск webhook тестов в локальной среде
- Изоляция тестов через моки
- Детерминированные результаты
- Поддержка параллельного выполнения

## Рекомендации

1. **Всегда используйте моки** для внешних зависимостей
2. **Тестируйте как успешные, так и ошибочные сценарии**
3. **Используйте соответствующие маркеры** для категоризации тестов
4. **Пишите тесты для новых функций** перед их реализацией
5. **Обновляйте тесты** при изменении API или логики

