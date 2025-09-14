"""
Тесты для модуля конфигурации.
"""
import os
import pytest
from unittest.mock import patch
import sys

# Добавляем src в путь для импортов
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from config import Config, config


@pytest.mark.config
class TestConfig:
    """Тесты для класса Config"""

    def test_config_initialization(self):
        """Тест инициализации конфигурации"""
        test_config = Config()
        assert hasattr(test_config, 'TELEGRAM_TOKEN')
        assert hasattr(test_config, 'NEUROAPI_API_KEY')
        assert hasattr(test_config, 'ENABLE_CONTEXT')
        assert hasattr(test_config, 'ENABLE_VOICE')

    def test_telegram_token_from_env(self):
        """Тест получения токена Telegram из переменных окружения"""
        with patch.dict(os.environ, {'TELEGRAM_TOKEN': 'test_token_123'}):
            test_config = Config()
            assert test_config.TELEGRAM_TOKEN == 'test_token_123'

    def test_neuroapi_config_from_env(self):
        """Тест получения конфигурации NeuroAPI из переменных окружения"""
        with patch.dict(os.environ, {
            'NEUROAPI_API_KEY': 'test_key',
            'NEUROAPI_TEMPERATURE': '0.5',
            'NEUROAPI_MAX_TOKENS': '2000'
        }):
            test_config = Config()
            assert test_config.NEUROAPI_API_KEY == 'test_key'
            assert test_config.NEUROAPI_TEMPERATURE == 0.5
            assert test_config.NEUROAPI_MAX_TOKENS == 2000

    def test_boolean_config_from_env(self):
        """Тест получения булевых значений из переменных окружения"""
        with patch.dict(os.environ, {
            'ENABLE_CONTEXT': 'true',
            'ENABLE_VOICE': 'false'
        }):
            test_config = Config()
            assert test_config.ENABLE_CONTEXT is True
            assert test_config.ENABLE_VOICE is False

    def test_boolean_config_case_insensitive(self):
        """Тест получения булевых значений с разным регистром"""
        with patch.dict(os.environ, {
            'ENABLE_CONTEXT': 'TRUE',
            'ENABLE_VOICE': 'False'
        }):
            test_config = Config()
            assert test_config.ENABLE_CONTEXT is True
            assert test_config.ENABLE_VOICE is False

    def test_webhook_config_from_env(self):
        """Тест получения конфигурации webhook из переменных окружения"""
        with patch.dict(os.environ, {
            'WEBHOOK_URL': 'https://test.example.com',
            'WEBHOOK_PORT': '8080',
            'WEBHOOK_HOST': '0.0.0.0',
            'WEBHOOK_PATH': '/test',
            'WEBHOOK_SECRET_TOKEN': 'test_secret'
        }):
            test_config = Config()
            assert test_config.WEBHOOK_URL == 'https://test.example.com'
            assert test_config.WEBHOOK_PORT == 8080
            assert test_config.WEBHOOK_HOST == '0.0.0.0'
            assert test_config.WEBHOOK_PATH == '/test'
            assert test_config.WEBHOOK_SECRET_TOKEN == 'test_secret'

    def test_voice_config_from_env(self):
        """Тест получения конфигурации голосовых функций из переменных окружения"""
        with patch.dict(os.environ, {
            'ENABLE_VOICE': 'true',
            'STT_LANGUAGE': 'en-US',
            'TTS_VOICE': 'john',
            'TTS_FORMAT': 'mp3',
            'AUDIO_MAX_DURATION_SEC': '120',
            'ENABLE_TTS_REPLY': 'true'
        }):
            test_config = Config()
            assert test_config.ENABLE_VOICE is True
            assert test_config.STT_LANGUAGE == 'en-US'
            assert test_config.TTS_VOICE == 'john'
            assert test_config.TTS_FORMAT == 'mp3'
            assert test_config.AUDIO_MAX_DURATION_SEC == 120
            assert test_config.ENABLE_TTS_REPLY is True

    def test_yandex_config_from_env(self):
        """Тест получения конфигурации Yandex Cloud из переменных окружения"""
        with patch.dict(os.environ, {
            'YC_FOLDER_ID': 'test_folder',
            'YC_API_KEY': 'test_api_key',
            'YC_IAM_TOKEN': 'test_iam_token',
            'YC_SA_KEY_FILE': '/path/to/key.json',
            'YC_SA_KEY_JSON': '{"test": "json"}',
            'YC_MODEL_URI': 'gpt://test_folder/yandexgpt/latest',
            'YC_TEMPERATURE': '0.4',
            'YC_MAX_TOKENS': '1000'
        }):
            test_config = Config()
            assert test_config.YC_FOLDER_ID == 'test_folder'
            assert test_config.YC_API_KEY == 'test_api_key'
            assert test_config.YC_IAM_TOKEN == 'test_iam_token'
            assert test_config.YC_SA_KEY_FILE == '/path/to/key.json'
            assert test_config.YC_SA_KEY_JSON == '{"test": "json"}'
            assert test_config.YC_MODEL_URI == 'gpt://test_folder/yandexgpt/latest'
            assert test_config.YC_TEMPERATURE == 0.4
            assert test_config.YC_MAX_TOKENS == 1000

    def test_default_values(self):
        """Тест значений по умолчанию"""
        # Очищаем переменные окружения
        env_vars_to_clear = [
            'NEUROAPI_TEMPERATURE', 'NEUROAPI_MAX_TOKENS',
            'ENABLE_CONTEXT', 'ENABLE_VOICE', 'LOG_LEVEL',
            'WEBHOOK_PORT', 'WEBHOOK_HOST', 'WEBHOOK_PATH',
            'STT_LANGUAGE', 'TTS_VOICE', 'TTS_FORMAT',
            'AUDIO_MAX_DURATION_SEC', 'ENABLE_TTS_REPLY',
            'YC_TEMPERATURE', 'YC_MAX_TOKENS'
        ]
        
        with patch.dict(os.environ, {}, clear=True):
            # Устанавливаем только необходимые переменные
            os.environ['TELEGRAM_TOKEN'] = 'test_token'
            os.environ['NEUROAPI_API_KEY'] = 'test_key'
            
            test_config = Config()
            
            # Проверяем значения по умолчанию
            assert test_config.NEUROAPI_TEMPERATURE == 0.7
            assert test_config.NEUROAPI_MAX_TOKENS == 5000
            assert test_config.ENABLE_CONTEXT is True
            assert test_config.LOG_LEVEL == 'INFO'
            assert test_config.WEBHOOK_PORT == 11844
            assert test_config.WEBHOOK_HOST == '0.0.0.0'
            assert test_config.WEBHOOK_PATH == '/bot'
            assert test_config.STT_LANGUAGE == 'ru-RU'
            assert test_config.TTS_VOICE == 'alena'
            assert test_config.TTS_FORMAT == 'oggopus'
            assert test_config.AUDIO_MAX_DURATION_SEC == 60
            assert test_config.ENABLE_TTS_REPLY is False
            assert test_config.YC_TEMPERATURE == 0.3
            assert test_config.YC_MAX_TOKENS == 800

    def test_api_endpoints(self):
        """Тест API эндпоинтов"""
        test_config = Config()
        
        assert test_config.YC_FOUNDATION_MODELS_ENDPOINT == "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        assert test_config.YC_STT_ENDPOINT == "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"
        assert test_config.YC_TTS_ENDPOINT == "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
        assert test_config.YC_IAM_ENDPOINT == "https://iam.api.cloud.yandex.net/iam/v1/tokens"

    def test_config_instance(self):
        """Тест глобального экземпляра конфигурации"""
        assert isinstance(config, Config)
        assert hasattr(config, 'TELEGRAM_TOKEN')
        assert hasattr(config, 'NEUROAPI_API_KEY')

    def test_none_values_for_missing_env(self):
        """Тест None значений для отсутствующих переменных окружения"""
        with patch.dict(os.environ, {}, clear=True):
            test_config = Config()
            
            assert test_config.TELEGRAM_TOKEN is None
            assert test_config.NEUROAPI_API_KEY is None
            assert test_config.YC_FOLDER_ID is None
            assert test_config.YC_API_KEY is None
            assert test_config.YC_IAM_TOKEN is None
            assert test_config.YC_SA_KEY_FILE is None
            assert test_config.YC_SA_KEY_JSON is None
            assert test_config.YC_MODEL_URI is None
            assert test_config.WEBHOOK_URL is None
            assert test_config.WEBHOOK_SECRET_TOKEN is None
            assert test_config.SSL_CERT_PATH is None
            assert test_config.SSL_KEY_PATH is None

    def test_invalid_numeric_values(self):
        """Тест обработки невалидных числовых значений"""
        with patch.dict(os.environ, {
            'NEUROAPI_TEMPERATURE': 'invalid',
            'NEUROAPI_MAX_TOKENS': 'not_a_number',
            'WEBHOOK_PORT': 'invalid_port',
            'AUDIO_MAX_DURATION_SEC': 'invalid_duration'
        }):
            with pytest.raises(ValueError):
                Config()

    def test_webhook_url_default(self):
        """Тест значения по умолчанию для WEBHOOK_URL"""
        with patch.dict(os.environ, {}, clear=True):
            test_config = Config()
            assert test_config.WEBHOOK_URL == "https://talkbot.skhlebnikov.ru"

    def test_ssl_paths_none(self):
        """Тест что SSL пути по умолчанию None"""
        test_config = Config()
        assert test_config.SSL_CERT_PATH is None
        assert test_config.SSL_KEY_PATH is None

