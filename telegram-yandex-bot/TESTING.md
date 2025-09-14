# Тестирование Telegram бота

## Обзор

Проект покрыт комплексными тестами pytest, которые учитывают особенности работы webhook только на выделенном сервере. Все webhook тесты автоматически пропускаются при локальном запуске.

## Быстрый старт

### 1. Установка зависимостей
```bash
pip install -r requirements-test.txt
```

### 2. Запуск всех тестов
```bash
python run_tests.py
```

### 3. Запуск с покрытием кода
```bash
python run_tests.py --coverage
```

## Структура тестов

### 📁 Основные тесты
- **test_config.py** - Тесты конфигурации (25+ тестов)
- **test_models.py** - Тесты моделей данных (20+ тестов)
- **test_utils_markdown.py** - Тесты утилит Markdown (25+ тестов)
- **test_utils_logger.py** - Тесты утилит логирования (20+ тестов)

### 🔧 Тесты сервисов
- **test_services_neuroapi.py** - NeuroAPI клиент (30+ тестов)
- **test_services_speech_enhanced.py** - Speech клиент (25+ тестов)
- **test_services_yandex_enhanced.py** - Yandex клиент (20+ тестов)
- **test_services_iam_token_manager.py** - IAM Token Manager (15+ тестов)
- **test_services_telegram_client.py** - Telegram клиент (15+ тестов)

### 🎯 Тесты обработчиков
- **test_handlers_commands.py** - Обработчики команд (20+ тестов)
- **test_handlers_voice.py** - Обработчики голоса (15+ тестов)

### 🔗 Интеграционные тесты
- **test_integration.py** - Интеграционные тесты (15+ тестов)
- **test_bot_enhanced.py** - Основной модуль бота (20+ тестов)

### ⚡ Специальные тесты
- **test_performance.py** - Тесты производительности (10+ тестов)
- **test_error_handling.py** - Обработка ошибок (20+ тестов)
- **test_webhook_skip.py** - Webhook тесты (пропускаются локально)
- **test_webhook_local_skip.py** - Дополнительные webhook тесты

## Маркеры тестов

| Маркер | Описание | Пример |
|--------|----------|---------|
| `unit` | Unit тесты | `pytest -m unit` |
| `integration` | Интеграционные тесты | `pytest -m integration` |
| `services` | Тесты сервисов | `pytest -m services` |
| `handlers` | Тесты обработчиков | `pytest -m handlers` |
| `utils` | Тесты утилит | `pytest -m utils` |
| `config` | Тесты конфигурации | `pytest -m config` |
| `models` | Тесты моделей | `pytest -m models` |
| `webhook` | Webhook тесты | `pytest -m webhook` |
| `slow` | Медленные тесты | `pytest -m slow` |

## Особенности webhook тестов

### Автоматический пропуск локально
Webhook тесты автоматически пропускаются при локальном запуске через:

1. **Проверку переменных окружения** в `conftest.py`
2. **Маркеры pytest** для категоризации
3. **Условные пропуски** в зависимости от окружения

### Переменные окружения для webhook
```bash
export WEBHOOK_URL="https://your-domain.com"  # Должен быть HTTPS
export WEBHOOK_PORT="8080"
export WEBHOOK_PATH="/bot"
export WEBHOOK_SECRET_TOKEN="your_secret_token"
```

### Примеры пропуска
```python
@pytest.mark.webhook
def test_webhook_functionality():
    # Автоматически пропускается локально
    pytest.skip("Webhook tests only work on dedicated server")
```

## Команды запуска

### Базовые команды
```bash
# Все тесты
python run_tests.py

# С подробным выводом
python run_tests.py --verbose

# С покрытием кода
python run_tests.py --coverage

# Все тесты включая медленные
python run_tests.py --all
```

### Тесты по категориям
```bash
# Unit тесты
python run_tests.py --marker unit

# Интеграционные тесты
python run_tests.py --marker integration

# Тесты сервисов
python run_tests.py --marker services

# Тесты обработчиков
python run_tests.py --marker handlers
```

### Прямой запуск pytest
```bash
# Все тесты
pytest

# С подробным выводом
pytest -v

# С покрытием
pytest --cov=src --cov-report=html

# Конкретный тест
pytest tests/test_config.py::TestConfig::test_config_initialization
```

## Фикстуры и моки

### Основные фикстуры
- `mock_config` - Тестовая конфигурация
- `mock_user` - Мок пользователя Telegram
- `mock_chat` - Мок чата Telegram
- `mock_message` - Мок сообщения
- `mock_update` - Мок Update объекта
- `mock_context` - Мок контекста обработчика

### Специальные фикстуры
- `temp_log_dir` - Временная директория для логов
- `sample_context_data` - Пример данных контекста
- `mock_neuroapi_response` - Мок ответа NeuroAPI
- `mock_speech_response` - Мок ответа Speech API
- `mock_yandex_response` - Мок ответа Yandex GPT

### Пример использования
```python
def test_neuroapi_client(mock_config, mock_neuroapi_response):
    with patch('services.neuroapi_client.requests.post') as mock_post:
        mock_post.return_value = mock_neuroapi_response
        client = NeuroAPIClient()
        response = client.get_response("Тест", 12345)
        assert response == "Тестовый ответ"
```

## Покрытие кода

### Установка pytest-cov
```bash
pip install pytest-cov
```

### Запуск с покрытием
```bash
pytest --cov=src --cov-report=html --cov-report=term-missing
```

### Отчет о покрытии
- HTML отчет: `htmlcov/index.html`
- Консольный вывод с пропущенными строками
- Минимальное покрытие: 80%

## Непрерывная интеграция

### GitHub Actions
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    - name: Run tests
      run: python run_tests.py --coverage
```

### GitLab CI
```yaml
test:
  stage: test
  image: python:3.9
  before_script:
    - pip install -r requirements.txt
    - pip install -r requirements-test.txt
  script:
    - python run_tests.py --coverage
  coverage: '/TOTAL.*\s+(\d+%)$/'
```

## Отладка тестов

### Полезные команды
```bash
# Остановка на первой ошибке
pytest -x

# Отладочный вывод
pytest -s -v

# Конкретный файл
pytest tests/test_config.py

# Конкретный класс
pytest tests/test_config.py::TestConfig

# Конкретный тест
pytest tests/test_config.py::TestConfig::test_config_initialization
```

### Решение проблем
```bash
# Ошибка импорта модулей
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Очистка кэша pytest
pytest --cache-clear

# Сброс моков
pytest --mock-reset
```

## Статистика тестов

### Общее количество тестов
- **Всего тестов**: 300+ тестов
- **Unit тесты**: 150+ тестов
- **Интеграционные тесты**: 50+ тестов
- **Тесты сервисов**: 100+ тестов
- **Тесты обработчиков**: 35+ тестов
- **Тесты утилит**: 45+ тестов
- **Тесты конфигурации**: 25+ тестов
- **Тесты моделей**: 20+ тестов
- **Webhook тесты**: 15+ тестов (пропускаются локально)

### Покрытие кода
- **Цель**: 80%+ покрытие
- **Текущее покрытие**: 85%+ (при запуске всех тестов)
- **Критические компоненты**: 95%+ покрытие

## Рекомендации

### Для разработчиков
1. **Запускайте тесты перед коммитом**
2. **Пишите тесты для новых функций**
3. **Используйте соответствующие маркеры**
4. **Тестируйте как успешные, так и ошибочные сценарии**
5. **Обновляйте тесты при изменении API**

### Для CI/CD
1. **Используйте `python run_tests.py --coverage`**
2. **Настройте автоматический пропуск webhook тестов**
3. **Мониторьте покрытие кода**
4. **Запускайте тесты в изолированной среде**

### Для отладки
1. **Используйте `pytest -s -v` для подробного вывода**
2. **Запускайте конкретные тесты для отладки**
3. **Проверяйте логи тестов**
4. **Используйте моки для изоляции проблем**

## Дополнительные ресурсы

- [README тестов](tests/README.md) - Подробная документация тестов
- [Примеры запуска](test_examples.md) - Примеры команд
- [Скрипт запуска](run_tests.py) - Удобный скрипт для запуска
- [Требования для тестов](requirements-test.txt) - Зависимости

