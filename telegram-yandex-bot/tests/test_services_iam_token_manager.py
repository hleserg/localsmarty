"""
Тесты для сервиса IAM Token Manager.
"""
import pytest
import sys
import os
import json
import time
from unittest.mock import patch, Mock, mock_open
from datetime import datetime, timedelta

# Добавляем src в путь для импортов
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from services.iam_token_manager import IamTokenManager, token_manager


@pytest.mark.services
class TestIamTokenManager:
    """Тесты для IAM Token Manager"""

    @pytest.fixture
    def manager(self, mock_config):
        """Фикстура для создания менеджера токенов"""
        return IamTokenManager()

    @pytest.fixture
    def sample_sa_key(self):
        """Фикстура с примером ключа сервисного аккаунта"""
        return {
            "id": "test_key_id",
            "service_account_id": "test_service_account_id",
            "private_key": "-----BEGIN PRIVATE KEY-----\ntest_private_key\n-----END PRIVATE KEY-----"
        }

    def test_manager_initialization(self, manager):
        """Тест инициализации менеджера"""
        assert manager._iam_token is None
        assert manager._expires_at is None
        assert manager._sa_key is None

    def test_load_sa_key_from_json(self, manager, sample_sa_key):
        """Тест загрузки ключа из JSON строки"""
        with patch('services.iam_token_manager.config') as mock_config:
            mock_config.YC_SA_KEY_JSON = json.dumps(sample_sa_key)
            
            result = manager._load_sa_key()
            
            assert result == sample_sa_key
            assert manager._sa_key == sample_sa_key

    def test_load_sa_key_from_file(self, manager, sample_sa_key):
        """Тест загрузки ключа из файла"""
        with patch('services.iam_token_manager.config') as mock_config:
            mock_config.YC_SA_KEY_JSON = None
            mock_config.YC_SA_KEY_FILE = '/path/to/key.json'
            
            with patch('builtins.open', mock_open(read_data=json.dumps(sample_sa_key))):
                result = manager._load_sa_key()
                
                assert result == sample_sa_key
                assert manager._sa_key == sample_sa_key

    def test_load_sa_key_no_source(self, manager):
        """Тест загрузки ключа без источника"""
        with patch('services.iam_token_manager.config') as mock_config:
            mock_config.YC_SA_KEY_JSON = None
            mock_config.YC_SA_KEY_FILE = None
            
            with pytest.raises(ValueError, match="Service account key is not provided"):
                manager._load_sa_key()

    def test_load_sa_key_invalid_json(self, manager):
        """Тест загрузки невалидного JSON ключа"""
        with patch('services.iam_token_manager.config') as mock_config:
            mock_config.YC_SA_KEY_JSON = "invalid json"
            
            with pytest.raises(ValueError, match="Invalid YC_SA_KEY_JSON"):
                manager._load_sa_key()

    def test_load_sa_key_missing_fields(self, manager):
        """Тест загрузки ключа с отсутствующими полями"""
        incomplete_key = {
            "id": "test_key_id",
            "service_account_id": "test_service_account_id"
            # Отсутствует private_key
        }
        
        with patch('services.iam_token_manager.config') as mock_config:
            mock_config.YC_SA_KEY_JSON = json.dumps(incomplete_key)
            
            with pytest.raises(ValueError, match="Missing field 'private_key'"):
                manager._load_sa_key()

    def test_load_sa_key_file_error(self, manager):
        """Тест обработки ошибки при чтении файла"""
        with patch('services.iam_token_manager.config') as mock_config:
            mock_config.YC_SA_KEY_JSON = None
            mock_config.YC_SA_KEY_FILE = '/path/to/key.json'
            
            with patch('builtins.open', side_effect=IOError("File not found")):
                with pytest.raises(IOError):
                    manager._load_sa_key()

    @patch('services.iam_token_manager.jwt.encode')
    def test_build_jwt_success(self, mock_jwt_encode, manager, sample_sa_key):
        """Тест успешного создания JWT токена"""
        mock_jwt_encode.return_value = "test_jwt_token"
        
        with patch('services.iam_token_manager.config') as mock_config:
            mock_config.YC_IAM_ENDPOINT = "https://test.endpoint/iam"
            
            manager._sa_key = sample_sa_key
            result = manager._build_jwt()
            
            assert result == "test_jwt_token"
            mock_jwt_encode.assert_called_once()

    @patch('services.iam_token_manager.jwt.encode')
    def test_build_jwt_ps256_fallback(self, mock_jwt_encode, manager, sample_sa_key):
        """Тест fallback на RS256 при ошибке PS256"""
        # Первый вызов с PS256 вызывает исключение, второй с RS256 успешен
        mock_jwt_encode.side_effect = [Exception("PS256 not supported"), "test_jwt_token"]
        
        with patch('services.iam_token_manager.config') as mock_config:
            mock_config.YC_IAM_ENDPOINT = "https://test.endpoint/iam"
            
            manager._sa_key = sample_sa_key
            result = manager._build_jwt()
            
            assert result == "test_jwt_token"
            assert mock_jwt_encode.call_count == 2

    def test_build_jwt_no_jwt_library(self, manager, sample_sa_key):
        """Тест ошибки при отсутствии библиотеки JWT"""
        with patch('services.iam_token_manager.jwt', side_effect=ImportError("No module named jwt")):
            manager._sa_key = sample_sa_key
            
            with pytest.raises(RuntimeError, match="PyJWT is required"):
                manager._build_jwt()

    @patch('services.iam_token_manager.jwt.encode')
    def test_build_jwt_bytes_return(self, mock_jwt_encode, manager, sample_sa_key):
        """Тест обработки bytes возвращаемого значения от PyJWT"""
        mock_jwt_encode.return_value = b"test_jwt_token"
        
        with patch('services.iam_token_manager.config') as mock_config:
            mock_config.YC_IAM_ENDPOINT = "https://test.endpoint/iam"
            
            manager._sa_key = sample_sa_key
            result = manager._build_jwt()
            
            assert result == "test_jwt_token"

    @patch('services.iam_token_manager.requests.post')
    def test_request_iam_token_success(self, mock_post, manager, mock_iam_token_response):
        """Тест успешного запроса IAM токена"""
        mock_post.return_value = mock_iam_token_response
        
        with patch.object(manager, '_build_jwt', return_value="test_jwt"):
            manager._request_iam_token()
            
            assert manager._iam_token == "test_iam_token_123"
            assert manager._expires_at is not None
            mock_post.assert_called_once()

    @patch('services.iam_token_manager.requests.post')
    def test_request_iam_token_network_error(self, mock_post, manager):
        """Тест обработки сетевой ошибки при запросе токена"""
        mock_post.side_effect = Exception("Network error")
        
        with patch.object(manager, '_build_jwt', return_value="test_jwt"):
            with pytest.raises(RuntimeError, match="Failed to obtain IAM token"):
                manager._request_iam_token()

    @patch('services.iam_token_manager.requests.post')
    def test_request_iam_token_invalid_response(self, mock_post, manager):
        """Тест обработки невалидного ответа"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"invalid": "response"}
        mock_post.return_value = mock_response
        
        with patch.object(manager, '_build_jwt', return_value="test_jwt"):
            with pytest.raises(RuntimeError, match="Invalid IAM token response"):
                manager._request_iam_token()

    @patch('services.iam_token_manager.requests.post')
    def test_request_iam_token_missing_fields(self, mock_post, manager):
        """Тест обработки ответа с отсутствующими полями"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "iamToken": "test_token"
            # Отсутствует expiresAt
        }
        mock_post.return_value = mock_response
        
        with patch.object(manager, '_build_jwt', return_value="test_jwt"):
            with pytest.raises(RuntimeError, match="Invalid IAM token response"):
                manager._request_iam_token()

    def test_get_token_first_time(self, manager):
        """Тест получения токена в первый раз"""
        with patch.object(manager, '_request_iam_token') as mock_request:
            manager._iam_token = "test_token"
            manager._expires_at = datetime.now() + timedelta(hours=1)
            
            result = manager.get_token()
            
            assert result == "test_token"
            mock_request.assert_called_once()

    def test_get_token_refresh_needed(self, manager):
        """Тест обновления токена при необходимости"""
        with patch.object(manager, '_request_iam_token') as mock_request:
            # Токен истекает через 2 минуты (меньше 5 минут)
            manager._iam_token = "old_token"
            manager._expires_at = datetime.now() + timedelta(minutes=2)
            
            # Мокаем новый токен после обновления
            def side_effect():
                manager._iam_token = "new_token"
                manager._expires_at = datetime.now() + timedelta(hours=1)
            
            mock_request.side_effect = side_effect
            
            result = manager.get_token()
            
            assert result == "new_token"
            mock_request.assert_called_once()

    def test_get_token_no_refresh_needed(self, manager):
        """Тест получения токена без необходимости обновления"""
        with patch.object(manager, '_request_iam_token') as mock_request:
            # Токен истекает через 10 минут (больше 5 минут)
            manager._iam_token = "valid_token"
            manager._expires_at = datetime.now() + timedelta(minutes=10)
            
            result = manager.get_token()
            
            assert result == "valid_token"
            mock_request.assert_not_called()

    def test_get_token_no_token(self, manager):
        """Тест получения токена когда его нет"""
        with patch.object(manager, '_request_iam_token') as mock_request:
            manager._iam_token = None
            manager._expires_at = None
            
            # Мокаем новый токен после запроса
            def side_effect():
                manager._iam_token = "new_token"
                manager._expires_at = datetime.now() + timedelta(hours=1)
            
            mock_request.side_effect = side_effect
            
            result = manager.get_token()
            
            assert result == "new_token"
            mock_request.assert_called_once()

    def test_get_token_no_expires_at(self, manager):
        """Тест получения токена когда нет времени истечения"""
        with patch.object(manager, '_request_iam_token') as mock_request:
            manager._iam_token = "test_token"
            manager._expires_at = None
            
            # Мокаем обновление времени истечения
            def side_effect():
                manager._expires_at = datetime.now() + timedelta(hours=1)
            
            mock_request.side_effect = side_effect
            
            result = manager.get_token()
            
            assert result == "test_token"
            mock_request.assert_called_once()

    def test_token_manager_singleton(self):
        """Тест что token_manager является синглтоном"""
        assert isinstance(token_manager, IamTokenManager)

    @patch('services.iam_token_manager.requests.post')
    def test_request_iam_token_expires_at_parsing(self, mock_post, manager):
        """Тест парсинга времени истечения токена"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "iamToken": "test_token",
            "expiresAt": "2024-12-31T23:59:59.123456Z"
        }
        mock_post.return_value = mock_response
        
        with patch.object(manager, '_build_jwt', return_value="test_jwt"):
            manager._request_iam_token()
            
            assert manager._iam_token == "test_token"
            assert manager._expires_at is not None
            assert manager._expires_at.year == 2024
            assert manager._expires_at.month == 12
            assert manager._expires_at.day == 31

    @patch('services.iam_token_manager.requests.post')
    def test_request_iam_token_expires_at_invalid_format(self, mock_post, manager):
        """Тест обработки невалидного формата времени истечения"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "iamToken": "test_token",
            "expiresAt": "invalid_date_format"
        }
        mock_post.return_value = mock_response
        
        with patch.object(manager, '_build_jwt', return_value="test_jwt"):
            with pytest.raises(ValueError):
                manager._request_iam_token()

    def test_jwt_payload_structure(self, manager, sample_sa_key):
        """Тест структуры JWT payload"""
        with patch('services.iam_token_manager.jwt.encode') as mock_jwt_encode, \
             patch('services.iam_token_manager.config') as mock_config, \
             patch('services.iam_token_manager.time.time', return_value=1000):
            
            mock_config.YC_IAM_ENDPOINT = "https://test.endpoint/iam"
            manager._sa_key = sample_sa_key
            
            manager._build_jwt()
            
            # Проверяем что jwt.encode был вызван с правильными параметрами
            call_args = mock_jwt_encode.call_args
            payload = call_args[0][1]
            headers = call_args[0][2]
            
            assert payload["aud"] == "https://test.endpoint/iam"
            assert payload["iss"] == "test_service_account_id"
            assert payload["sub"] == "test_service_account_id"
            assert payload["iat"] == 1000
            assert payload["exp"] == 4600  # 1000 + 3600
            
            assert headers["kid"] == "test_key_id"
            assert headers["typ"] == "JWT"

