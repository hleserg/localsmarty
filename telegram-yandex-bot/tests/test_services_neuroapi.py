"""
Тесты для сервиса NeuroAPI клиента.
"""
import pytest
import sys
import os
import json
import tempfile
from unittest.mock import patch, Mock, mock_open
from datetime import datetime

# Добавляем src в путь для импортов
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from services.neuroapi_client import NeuroAPIClient, get_gpt_response


@pytest.mark.services
class TestNeuroAPIClient:
    """Тесты для NeuroAPI клиента"""

    @pytest.fixture
    def client(self, mock_config):
        """Фикстура для создания клиента NeuroAPI"""
        with patch('services.neuroapi_client.os.path.exists', return_value=False):
            return NeuroAPIClient()

    def test_client_initialization(self, client):
        """Тест инициализации клиента"""
        assert client.api_key == 'test_neuroapi_key'
        assert client.endpoint == "https://neuroapi.host/v1/chat/completions"
        assert client.model == "gpt-5"
        assert isinstance(client.chat_contexts, dict)
        assert client.context_file == "/app/logs/chat_contexts.json"

    def test_get_headers_success(self, client):
        """Тест получения заголовков для успешного запроса"""
        headers = client._get_headers()
        
        expected_headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer test_neuroapi_key"
        }
        assert headers == expected_headers

    def test_get_headers_no_api_key(self):
        """Тест получения заголовков без API ключа"""
        with patch('services.neuroapi_client.config') as mock_config:
            mock_config.NEUROAPI_API_KEY = None
            
            with patch('services.neuroapi_client.os.path.exists', return_value=False):
                client = NeuroAPIClient()
                
                with pytest.raises(ValueError, match="NEUROAPI_API_KEY is not set"):
                    client._get_headers()

    def test_prepare_messages_regular_chat(self, client):
        """Тест подготовки сообщений для обычного чата"""
        messages = client._prepare_messages("Привет", 12345)
        
        assert len(messages) >= 2
        assert messages[0]["role"] == "system"
        assert messages[-1]["role"] == "user"
        assert messages[-1]["content"] == "Привет"

    def test_prepare_messages_business_chat(self, client):
        """Тест подготовки сообщений для бизнес-чата"""
        messages = client._prepare_messages("Здравствуйте", 12345, is_business_message=True, business_connection_id="test_connection")
        
        assert len(messages) >= 2
        assert messages[0]["role"] == "system"
        assert messages[-1]["role"] == "user"
        assert messages[-1]["content"] == "Здравствуйте"

    def test_prepare_messages_with_context(self, client, sample_context_data):
        """Тест подготовки сообщений с контекстом"""
        # Устанавливаем контекст
        client.chat_contexts = sample_context_data
        
        messages = client._prepare_messages("Как дела?", 12345)
        
        # Должно быть системное сообщение + контекст + новое сообщение
        assert len(messages) >= 3
        assert messages[0]["role"] == "system"
        assert messages[-1]["role"] == "user"
        assert messages[-1]["content"] == "Как дела?"

    def test_prepare_messages_business_with_context(self, client, sample_context_data):
        """Тест подготовки сообщений для бизнес-чата с контекстом"""
        # Устанавливаем контекст для бизнес-чата
        client.chat_contexts = sample_context_data
        
        messages = client._prepare_messages("Вопрос", 67890, is_business_message=True, business_connection_id="test_connection")
        
        assert len(messages) >= 3
        assert messages[0]["role"] == "system"
        assert messages[-1]["role"] == "user"
        assert messages[-1]["content"] == "Вопрос"

    def test_update_context_regular_chat(self, client):
        """Тест обновления контекста для обычного чата"""
        client._update_context(12345, "Привет", "Привет! Как дела?")
        
        assert 12345 in client.chat_contexts
        context = client.chat_contexts[12345]
        assert len(context) == 2
        assert context[0]["role"] == "user"
        assert context[0]["content"] == "Привет"
        assert context[1]["role"] == "assistant"
        assert context[1]["content"] == "Привет! Как дела?"

    def test_update_context_business_chat(self, client):
        """Тест обновления контекста для бизнес-чата"""
        client._update_context(12345, "Здравствуйте", "Здравствуйте! Я ИИ-ассистент Сергея.", is_business_message=True, business_connection_id="test_connection")
        
        context_key = "business_test_connection_12345"
        assert context_key in client.chat_contexts
        context = client.chat_contexts[context_key]
        assert len(context) == 2

    def test_update_context_disabled(self, client):
        """Тест обновления контекста когда он отключен"""
        with patch('services.neuroapi_client.config') as mock_config:
            mock_config.ENABLE_CONTEXT = False
            
            client._update_context(12345, "Привет", "Привет!")
            
            # Контекст не должен обновиться
            assert 12345 not in client.chat_contexts

    def test_update_context_trimming(self, client):
        """Тест обрезания контекста при превышении лимита"""
        # Добавляем много сообщений
        for i in range(15):  # 15 пар = 30 сообщений
            client._update_context(12345, f"Сообщение {i}", f"Ответ {i}")
        
        context = client.chat_contexts[12345]
        # Должно остаться только последние 20 сообщений
        assert len(context) == 20

    def test_load_contexts_file_exists(self, temp_context_file, sample_context_data):
        """Тест загрузки контекста из существующего файла"""
        with patch('services.neuroapi_client.os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=json.dumps(sample_context_data, ensure_ascii=False))):
            
            client = NeuroAPIClient()
            assert client.chat_contexts == sample_context_data

    def test_load_contexts_file_not_exists(self):
        """Тест загрузки контекста когда файл не существует"""
        with patch('services.neuroapi_client.os.path.exists', return_value=False):
            client = NeuroAPIClient()
            assert client.chat_contexts == {}

    def test_load_contexts_file_error(self):
        """Тест обработки ошибки при загрузке контекста"""
        with patch('services.neuroapi_client.os.path.exists', return_value=True), \
             patch('builtins.open', side_effect=IOError("File error")):
            
            client = NeuroAPIClient()
            assert client.chat_contexts == {}

    def test_save_contexts(self, client, temp_log_dir):
        """Тест сохранения контекста в файл"""
        client.context_file = os.path.join(temp_log_dir, "test_contexts.json")
        client.chat_contexts = {"12345": [{"role": "user", "content": "test"}]}
        
        client._save_contexts()
        
        # Проверяем что файл был создан
        assert os.path.exists(client.context_file)
        
        # Проверяем содержимое файла
        with open(client.context_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        assert saved_data == client.chat_contexts

    def test_save_contexts_error(self, client):
        """Тест обработки ошибки при сохранении контекста"""
        client.context_file = "/invalid/path/contexts.json"
        client.chat_contexts = {"12345": [{"role": "user", "content": "test"}]}
        
        # Не должно вызывать исключение
        client._save_contexts()

    @patch('services.neuroapi_client.requests.post')
    def test_get_response_success(self, mock_post, client, mock_neuroapi_response):
        """Тест успешного получения ответа от NeuroAPI"""
        mock_post.return_value = mock_neuroapi_response
        
        response = client.get_response("Привет", 12345)
        
        assert response == "Тестовый ответ от GPT-5"
        mock_post.assert_called_once()

    @patch('services.neuroapi_client.requests.post')
    def test_get_response_empty_input(self, mock_post, client):
        """Тест обработки пустого ввода"""
        response = client.get_response("", 12345)
        
        assert response == "Ошибка: пустой ввод"
        mock_post.assert_not_called()

    @patch('services.neuroapi_client.requests.post')
    def test_get_response_long_message(self, mock_post, client, mock_neuroapi_response):
        """Тест обработки длинного сообщения"""
        mock_post.return_value = mock_neuroapi_response
        
        long_message = "A" * 5000  # Длинное сообщение
        response = client.get_response(long_message, 12345)
        
        # Проверяем что сообщение было обрезано
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        assert len(payload['messages'][-1]['content']) == 4000

    @patch('services.neuroapi_client.requests.post')
    def test_get_response_api_error(self, mock_post, client):
        """Тест обработки ошибки API"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response
        
        response = client.get_response("Тест", 12345)
        
        assert "Извините, произошла ошибка" in response

    @patch('services.neuroapi_client.requests.post')
    def test_get_response_business_api_error(self, mock_post, client):
        """Тест обработки ошибки API для бизнес-сообщений"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response
        
        response = client.get_response("Тест", 12345, is_business_message=True, business_connection_id="test_connection")
        
        assert "ИИ-ассистент Сергея" in response

    @patch('services.neuroapi_client.requests.post')
    def test_get_response_empty_response(self, mock_post, client):
        """Тест обработки пустого ответа от API"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": ""  # Пустой ответ
                }
            }]
        }
        mock_post.return_value = mock_response
        
        response = client.get_response("Тест", 12345)
        
        assert "не смог сгенерировать ответ" in response

    @patch('services.neuroapi_client.requests.post')
    def test_get_response_business_empty_response(self, mock_post, client):
        """Тест обработки пустого ответа для бизнес-сообщений"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": ""  # Пустой ответ
                }
            }]
        }
        mock_post.return_value = mock_response
        
        response = client.get_response("Тест", 12345, is_business_message=True, business_connection_id="test_connection")
        
        assert "ИИ-ассистент Сергея" in response

    @patch('services.neuroapi_client.requests.post')
    def test_get_response_timeout(self, mock_post, client):
        """Тест обработки таймаута"""
        mock_post.side_effect = Exception("Timeout")
        
        response = client.get_response("Тест", 12345)
        
        assert "Превышено время ожидания" in response

    @patch('services.neuroapi_client.requests.post')
    def test_get_response_business_timeout(self, mock_post, client):
        """Тест обработки таймаута для бизнес-сообщений"""
        mock_post.side_effect = Exception("Timeout")
        
        response = client.get_response("Тест", 12345, is_business_message=True, business_connection_id="test_connection")
        
        assert "ИИ-ассистент Сергея" in response

    @patch('services.neuroapi_client.requests.post')
    def test_get_response_retry_logic(self, mock_post, client):
        """Тест логики повторных попыток при пустом ответе"""
        # Первый ответ пустой, второй успешный
        empty_response = Mock()
        empty_response.status_code = 200
        empty_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": ""
                }
            }]
        }
        
        success_response = Mock()
        success_response.status_code = 200
        success_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "Успешный ответ"
                }
            }]
        }
        
        mock_post.side_effect = [empty_response, success_response]
        
        response = client.get_response("Тест", 12345)
        
        assert response == "Успешный ответ"
        assert mock_post.call_count == 2

    def test_get_gpt_response_function(self, mock_neuroapi_response):
        """Тест функции get_gpt_response для обратной совместимости"""
        with patch('services.neuroapi_client.requests.post', return_value=mock_neuroapi_response):
            response = get_gpt_response("Тест", 12345)
            assert response == "Тестовый ответ от GPT-5"

    def test_business_message_system_prompt_first_time(self, client):
        """Тест системного промпта для первого бизнес-сообщения"""
        messages = client._prepare_messages("Первое сообщение", 12345, is_business_message=True, business_connection_id="test_connection")
        
        system_content = messages[0]["content"]
        assert "ИИ-ассистент Сергея" in system_content
        assert "бизнес-чате" in system_content

    def test_business_message_system_prompt_with_context(self, client, sample_context_data):
        """Тест системного промпта для бизнес-сообщения с контекстом"""
        client.chat_contexts = sample_context_data
        
        messages = client._prepare_messages("Последующее сообщение", 67890, is_business_message=True, business_connection_id="test_connection")
        
        system_content = messages[0]["content"]
        assert "ИИ-ассистент Сергея" in system_content
        assert "Продолжай общение" in system_content

