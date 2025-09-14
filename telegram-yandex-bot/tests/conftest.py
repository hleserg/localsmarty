"""
Конфигурация pytest с фикстурами для тестирования Telegram бота.
Учитывает особенности работы webhook только на выделенном сервере.
"""
import os
import sys
import pytest
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

# Добавляем src в путь для импортов
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

# Импорты для фикстур
from telegram import Update, Message, Chat, User, Voice, BusinessMessage, BusinessConnection
from telegram.ext import ContextTypes


@pytest.fixture(scope="session")
def test_config():
    """Фикстура с тестовой конфигурацией"""
    return {
        'TELEGRAM_TOKEN': 'test_token_123',
        'NEUROAPI_API_KEY': 'test_neuroapi_key',
        'NEUROAPI_TEMPERATURE': 0.7,
        'NEUROAPI_MAX_TOKENS': 1000,
        'ENABLE_CONTEXT': True,
        'ENABLE_VOICE': True,
        'LOG_LEVEL': 'INFO',
        'WEBHOOK_URL': 'https://test.example.com',
        'WEBHOOK_PORT': 8080,
        'WEBHOOK_HOST': '0.0.0.0',
        'WEBHOOK_PATH': '/test',
        'WEBHOOK_SECRET_TOKEN': 'test_secret',
        'STT_LANGUAGE': 'ru-RU',
        'TTS_VOICE': 'alena',
        'TTS_FORMAT': 'oggopus',
        'AUDIO_MAX_DURATION_SEC': 60,
        'ENABLE_TTS_REPLY': False,
        'YC_FOLDER_ID': 'test_folder',
        'YC_API_KEY': 'test_yc_key',
        'YC_IAM_TOKEN': None,
        'YC_SA_KEY_FILE': None,
        'YC_SA_KEY_JSON': None,
        'YC_MODEL_URI': 'gpt://test_folder/yandexgpt/latest',
        'YC_TEMPERATURE': 0.3,
        'YC_MAX_TOKENS': 800,
        'YC_FOUNDATION_MODELS_ENDPOINT': 'https://test.endpoint/completion',
        'YC_STT_ENDPOINT': 'https://test.endpoint/stt',
        'YC_TTS_ENDPOINT': 'https://test.endpoint/tts',
        'YC_IAM_ENDPOINT': 'https://test.endpoint/iam'
    }


@pytest.fixture
def mock_config(test_config):
    """Мок конфигурации для тестов"""
    with patch('config.config') as mock:
        for key, value in test_config.items():
            setattr(mock, key, value)
        yield mock


@pytest.fixture
def mock_user():
    """Фикстура для создания мока пользователя Telegram"""
    user = Mock(spec=User)
    user.id = 12345
    user.username = "testuser"
    user.first_name = "Test"
    user.last_name = "User"
    user.is_bot = False
    return user


@pytest.fixture
def mock_chat():
    """Фикстура для создания мока чата Telegram"""
    chat = Mock(spec=Chat)
    chat.id = 67890
    chat.type = "private"
    chat.title = None
    return chat


@pytest.fixture
def mock_message(mock_user, mock_chat):
    """Фикстура для создания мока сообщения Telegram"""
    message = Mock(spec=Message)
    message.message_id = 1
    message.from_user = mock_user
    message.chat = mock_chat
    message.text = "Тестовое сообщение"
    message.date = datetime.now()
    message.voice = None
    message.audio = None
    return message


@pytest.fixture
def mock_voice():
    """Фикстура для создания мока голосового сообщения"""
    voice = Mock(spec=Voice)
    voice.file_id = "test_voice_file_id"
    voice.duration = 5
    voice.file_size = 1024
    voice.mime_type = "audio/ogg"
    return voice


@pytest.fixture
def mock_business_connection():
    """Фикстура для создания мока бизнес-соединения"""
    connection = Mock(spec=BusinessConnection)
    connection.id = "test_business_connection_id"
    connection.user_chat_id = 11111
    connection.user_id = 22222
    connection.is_enabled = True
    return connection


@pytest.fixture
def mock_business_message(mock_user, mock_chat, mock_business_connection):
    """Фикстура для создания мока бизнес-сообщения"""
    business_message = Mock(spec=BusinessMessage)
    business_message.message_id = 2
    business_message.from_user = mock_user
    business_message.chat = mock_chat
    business_message.business_connection_id = mock_business_connection.id
    business_message.text = "Тестовое бизнес-сообщение"
    business_message.date = datetime.now()
    return business_message


@pytest.fixture
def mock_update(mock_message):
    """Фикстура для создания мока Update объекта"""
    update = Mock(spec=Update)
    update.update_id = 1
    update.message = mock_message
    update.business_message = None
    update.effective_chat = mock_message.chat
    update.effective_user = mock_message.from_user
    return update


@pytest.fixture
def mock_business_update(mock_business_message):
    """Фикстура для создания мока Update объекта с бизнес-сообщением"""
    update = Mock(spec=Update)
    update.update_id = 2
    update.message = None
    update.business_message = mock_business_message
    update.effective_chat = mock_business_message.chat
    update.effective_user = mock_business_message.from_user
    return update


@pytest.fixture
def mock_context():
    """Фикстура для создания мока Context объекта"""
    context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    context.bot = Mock()
    context.bot.send_message = Mock()
    context.bot.send_chat_action = Mock()
    context.bot.get_file = Mock()
    return context


@pytest.fixture
def temp_log_dir():
    """Фикстура для создания временной директории логов"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def mock_requests_response():
    """Фикстура для создания мока HTTP ответа"""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {"result": "test_response"}
    response.text = "test_response"
    response.content = b"test_content"
    return response


@pytest.fixture
def mock_neuroapi_response():
    """Фикстура для создания мока ответа NeuroAPI"""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "choices": [{
            "message": {
                "content": "Тестовый ответ от GPT-5"
            }
        }]
    }
    return response


@pytest.fixture
def mock_yandex_response():
    """Фикстура для создания мока ответа Yandex GPT"""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "result": {
            "alternatives": [{
                "message": {
                    "text": "Тестовый ответ от Yandex GPT"
                }
            }]
        }
    }
    return response


@pytest.fixture
def mock_speech_response():
    """Фикстура для создания мока ответа Speech API"""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "result": "Распознанный текст"
    }
    response.content = b"fake_audio_data"
    return response


@pytest.fixture
def mock_iam_token_response():
    """Фикстура для создания мока ответа IAM токена"""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "iamToken": "test_iam_token_123",
        "expiresAt": (datetime.now() + timedelta(hours=1)).isoformat() + "Z"
    }
    return response


@pytest.fixture
def sample_context_data():
    """Фикстура с примером данных контекста чата"""
    return {
        "12345": [
            {"role": "user", "content": "Привет"},
            {"role": "assistant", "content": "Привет! Как дела?"},
            {"role": "user", "content": "Хорошо, спасибо"},
            {"role": "assistant", "content": "Отлично!"}
        ],
        "business_test_connection_67890": [
            {"role": "user", "content": "Здравствуйте"},
            {"role": "assistant", "content": "Здравствуйте! Я ИИ-ассистент Сергея."}
        ]
    }


@pytest.fixture
def temp_context_file(temp_log_dir, sample_context_data):
    """Фикстура для создания временного файла контекста"""
    context_file = os.path.join(temp_log_dir, "chat_contexts.json")
    with open(context_file, 'w', encoding='utf-8') as f:
        json.dump(sample_context_data, f, ensure_ascii=False, indent=2)
    return context_file


@pytest.fixture
def mock_file_download():
    """Фикстура для мока загрузки файла"""
    file_mock = Mock()
    file_mock.download_to_memory = Mock()
    return file_mock


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Автоматическая настройка тестовой среды"""
    # Устанавливаем переменные окружения для тестов
    os.environ['TELEGRAM_TOKEN'] = 'test_token_123'
    os.environ['NEUROAPI_API_KEY'] = 'test_neuroapi_key'
    os.environ['ENABLE_CONTEXT'] = 'true'
    os.environ['ENABLE_VOICE'] = 'true'
    os.environ['LOG_LEVEL'] = 'INFO'
    
    yield
    
    # Очистка после тестов
    test_env_vars = [
        'TELEGRAM_TOKEN', 'NEUROAPI_API_KEY', 'ENABLE_CONTEXT', 
        'ENABLE_VOICE', 'LOG_LEVEL'
    ]
    for var in test_env_vars:
        if var in os.environ:
            del os.environ[var]


@pytest.fixture
def skip_webhook_tests():
    """Фикстура для пропуска тестов webhook локально"""
    def _skip_if_local():
        webhook_url = os.getenv('WEBHOOK_URL', '')
        if not webhook_url or 'localhost' in webhook_url or '127.0.0.1' in webhook_url:
            pytest.skip("Webhook tests skipped locally - only work on dedicated server")
    return _skip_if_local


# Маркеры для категоризации тестов
def pytest_configure(config):
    """Конфигурация pytest с маркерами"""
    config.addinivalue_line(
        "markers", "webhook: mark test as requiring webhook (skip locally)"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )


def pytest_collection_modifyitems(config, items):
    """Модификация коллекции тестов для пропуска webhook тестов локально"""
    webhook_url = os.getenv('WEBHOOK_URL', '')
    skip_webhook = not webhook_url or 'localhost' in webhook_url or '127.0.0.1' in webhook_url
    
    for item in items:
        if "webhook" in item.keywords and skip_webhook:
            item.add_marker(pytest.mark.skip(reason="Webhook tests skipped locally"))

