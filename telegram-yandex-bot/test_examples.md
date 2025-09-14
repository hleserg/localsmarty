# Примеры запуска тестов

## Базовые команды

### Запуск всех тестов
```bash
python run_tests.py
```

### Запуск с подробным выводом
```bash
python run_tests.py --verbose
```

### Запуск с покрытием кода
```bash
python run_tests.py --coverage
```

## Запуск тестов по категориям

### Unit тесты
```bash
python run_tests.py --marker unit
```

### Интеграционные тесты
```bash
python run_tests.py --marker integration
```

### Тесты сервисов
```bash
python run_tests.py --marker services
```

### Тесты обработчиков
```bash
python run_tests.py --marker handlers
```

### Тесты утилит
```bash
python run_tests.py --marker utils
```

### Тесты конфигурации
```bash
python run_tests.py --marker config
```

### Тесты моделей
```bash
python run_tests.py --marker models
```

## Специальные режимы

### Включение медленных тестов
```bash
python run_tests.py --slow
```

### Запуск всех тестов включая медленные
```bash
python run_tests.py --all
```

### Webhook тесты (только на сервере)
```bash
python run_tests.py --marker webhook
```

## Комбинированные команды

### Unit тесты с покрытием
```bash
python run_tests.py --marker unit --coverage
```

### Интеграционные тесты с подробным выводом
```bash
python run_tests.py --marker integration --verbose
```

### Все тесты с покрытием и подробным выводом
```bash
python run_tests.py --all --coverage --verbose
```

## Прямой запуск pytest

### Базовый запуск
```bash
pytest
```

### С подробным выводом
```bash
pytest -v
```

### С покрытием кода
```bash
pytest --cov=src --cov-report=html
```

### Конкретный тест
```bash
pytest tests/test_config.py::TestConfig::test_config_initialization
```

### Тесты с определенным маркером
```bash
pytest -m unit
pytest -m integration
pytest -m services
```

### Исключение медленных тестов
```bash
pytest -m "not slow"
```

### Исключение webhook тестов
```bash
pytest -m "not webhook"
```

## Отладка тестов

### Запуск с остановкой на первой ошибке
```bash
pytest -x
```

### Запуск с отладочным выводом
```bash
pytest -s -v
```

### Запуск конкретного файла
```bash
pytest tests/test_config.py
```

### Запуск конкретного класса
```bash
pytest tests/test_config.py::TestConfig
```

## Параллельный запуск

### Установка pytest-xdist
```bash
pip install pytest-xdist
```

### Запуск в несколько процессов
```bash
pytest -n auto
pytest -n 4  # 4 процесса
```

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

## Переменные окружения для тестов

### Локальная разработка
```bash
export TELEGRAM_TOKEN="test_token"
export NEUROAPI_API_KEY="test_key"
export ENABLE_CONTEXT="true"
export ENABLE_VOICE="true"
export LOG_LEVEL="INFO"
```

### Серверная среда (для webhook тестов)
```bash
export WEBHOOK_URL="https://your-domain.com"
export WEBHOOK_PORT="8080"
export WEBHOOK_PATH="/bot"
export WEBHOOK_SECRET_TOKEN="your_secret_token"
```

## Полезные команды

### Показать все маркеры
```bash
pytest --markers
```

### Показать доступные тесты
```bash
pytest --collect-only
```

### Запуск тестов с профилированием
```bash
pytest --durations=10
```

### Запуск тестов с отчетом о покрытии
```bash
pytest --cov=src --cov-report=term-missing --cov-report=html
```

### Запуск тестов с фильтрацией по имени
```bash
pytest -k "test_config"
pytest -k "not test_webhook"
```

## Решение проблем

### Ошибка импорта модулей
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

### Ошибки с асинхронными тестами
```bash
pytest --asyncio-mode=auto
```

### Проблемы с моками
```bash
pytest --mock-reset
```

### Очистка кэша pytest
```bash
pytest --cache-clear
```

