"""
Расширенные тесты для сервиса Yandex клиента.
"""
import pytest
import sys
import os
from unittest.mock import patch, Mock

# Добавляем src в путь для импортов
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from services.yandex_client import YandexClient


@pytest.mark.services
class TestYandexClientEnhanced:
    """Расширенные тесты для Yandex клиента"""

    @pytest.fixture
    def client(self, mock_config):
        """Фикстура для создания клиента Yandex"""
        return YandexClient()

    def test_client_initialization(self, client):
        """Тест инициализации клиента"""
        assert client.api_key == 'test_yc_key'
        assert client.folder_id == 'test_folder'
        assert client.model_uri == 'gpt://test_folder/yandexgpt/latest'
        assert client.endpoint == 'https://test.endpoint/completion'
        assert client.temperature == 0.3
        assert client.max_tokens == 800
        assert isinstance(client.chat_contexts, dict)

    def test_get_headers_with_api_key(self, client):
        """Тест получения заголовков с API ключом"""
        headers = client._get_headers()
        
        expected_headers = {
            "Authorization": "Api-Key test_yc_key",
            "Content-Type": "application/json"
        }
        assert headers == expected_headers

    def test_get_headers_with_iam_token(self, client):
        """Тест получения заголовков с IAM токеном"""
        with patch('services.yandex_client.config') as mock_config:
            mock_config.YC_API_KEY = None
            mock_config.YC_IAM_TOKEN = 'test_iam_token'
            
            headers = client._get_headers()
            
            expected_headers = {
                "Authorization": "Bearer test_iam_token",
                "Content-Type": "application/json"
            }
            assert headers == expected_headers

    def test_get_headers_no_credentials(self, client):
        """Тест получения заголовков без учетных данных"""
        with patch('services.yandex_client.config') as mock_config:
            mock_config.YC_API_KEY = None
            mock_config.YC_IAM_TOKEN = None
            
            with pytest.raises(ValueError, match="No API key or IAM token provided"):
                client._get_headers()

    def test_prepare_messages_regular_chat(self, client):
        """Тест подготовки сообщений для обычного чата"""
        messages = client._prepare_messages("Привет", 12345)
        
        assert len(messages) >= 2
        assert messages[0]["role"] == "system"
        assert messages[-1]["role"] == "user"
        assert messages[-1]["text"] == "Привет"

    def test_prepare_messages_with_context(self, client, sample_context_data):
        """Тест подготовки сообщений с контекстом"""
        # Устанавливаем контекст
        client.chat_contexts = sample_context_data
        
        messages = client._prepare_messages("Как дела?", 12345)
        
        # Должно быть системное сообщение + контекст + новое сообщение
        assert len(messages) >= 3
        assert messages[0]["role"] == "system"
        assert messages[-1]["role"] == "user"
        assert messages[-1]["text"] == "Как дела?"

    def test_prepare_messages_context_disabled(self, client, sample_context_data):
        """Тест подготовки сообщений когда контекст отключен"""
        with patch('services.yandex_client.config') as mock_config:
            mock_config.ENABLE_CONTEXT = False
            
            # Устанавливаем контекст
            client.chat_contexts = sample_context_data
            
            messages = client._prepare_messages("Привет", 12345)
            
            # Должно быть только системное сообщение + новое сообщение
            assert len(messages) == 2
            assert messages[0]["role"] == "system"
            assert messages[-1]["role"] == "user"

    def test_update_context_regular_chat(self, client):
        """Тест обновления контекста для обычного чата"""
        client._update_context(12345, "Привет", "Привет! Как дела?")
        
        assert 12345 in client.chat_contexts
        context = client.chat_contexts[12345]
        assert len(context) == 2
        assert context[0]["role"] == "user"
        assert context[0]["text"] == "Привет"
        assert context[1]["role"] == "assistant"
        assert context[1]["text"] == "Привет! Как дела?"

    def test_update_context_disabled(self, client):
        """Тест обновления контекста когда он отключен"""
        with patch('services.yandex_client.config') as mock_config:
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

    @patch('services.yandex_client.requests.post')
    def test_get_response_success(self, mock_post, client, mock_yandex_response):
        """Тест успешного получения ответа от Yandex GPT"""
        mock_post.return_value = mock_yandex_response
        
        response = client.get_response("Привет", 12345)
        
        assert response == "Тестовый ответ от Yandex GPT"
        mock_post.assert_called_once()

    @patch('services.yandex_client.requests.post')
    def test_get_response_empty_input(self, mock_post, client):
        """Тест обработки пустого ввода"""
        response = client.get_response("", 12345)
        
        assert response == "Ошибка: пустой ввод"
        mock_post.assert_not_called()

    @patch('services.yandex_client.requests.post')
    def test_get_response_api_error(self, mock_post, client):
        """Тест обработки ошибки API"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response
        
        response = client.get_response("Тест", 12345)
        
        assert "Извините, произошла ошибка" in response

    @patch('services.yandex_client.requests.post')
    def test_get_response_network_error(self, mock_post, client):
        """Тест обработки сетевой ошибки"""
        mock_post.side_effect = Exception("Network error")
        
        response = client.get_response("Тест", 12345)
        
        assert "Извините, произошла ошибка" in response

    @patch('services.yandex_client.requests.post')
    def test_get_response_invalid_response(self, mock_post, client):
        """Тест обработки невалидного ответа"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"invalid": "response"}
        mock_post.return_value = mock_response
        
        response = client.get_response("Тест", 12345)
        
        assert "Извините, произошла ошибка" in response

    @patch('services.yandex_client.requests.post')
    def test_get_response_request_params(self, mock_post, client, mock_yandex_response):
        """Тест параметров запроса"""
        mock_post.return_value = mock_yandex_response
        
        client.get_response("Тест", 12345)
        
        # Проверяем параметры запроса
        call_args = mock_post.call_args
        assert call_args[0][0] == client.endpoint
        
        # Проверяем заголовки
        headers = call_args[1]['headers']
        assert 'Authorization' in headers
        assert 'Content-Type' in headers
        
        # Проверяем JSON payload
        json_data = call_args[1]['json']
        assert 'modelUri' in json_data
        assert 'completionOptions' in json_data
        assert 'messages' in json_data

    def test_context_management_multiple_chats(self, client):
        """Тест управления контекстом для нескольких чатов"""
        # Обновляем контекст для разных чатов
        client._update_context(12345, "Привет", "Привет!")
        client._update_context(67890, "Здравствуйте", "Здравствуйте!")
        
        # Проверяем что контексты изолированы
        assert 12345 in client.chat_contexts
        assert 67890 in client.chat_contexts
        
        context_1 = client.chat_contexts[12345]
        context_2 = client.chat_contexts[67890]
        
        assert len(context_1) == 2
        assert len(context_2) == 2
        assert context_1[0]["text"] == "Привет"
        assert context_2[0]["text"] == "Здравствуйте"

    def test_context_management_large_context(self, client):
        """Тест управления большим контекстом"""
        # Добавляем много сообщений
        for i in range(25):  # 25 пар = 50 сообщений
            client._update_context(12345, f"Сообщение {i}", f"Ответ {i}")
        
        context = client.chat_contexts[12345]
        # Должно остаться только последние 20 сообщений
        assert len(context) == 20
        
        # Проверяем что остались последние сообщения
        assert context[0]["text"] == "Сообщение 15"
        assert context[-1]["text"] == "Ответ 24"

    def test_prepare_messages_system_prompt(self, client):
        """Тест системного промпта"""
        messages = client._prepare_messages("Тест", 12345)
        
        system_message = messages[0]
        assert system_message["role"] == "system"
        assert "полезный Telegram-бот" in system_message["text"]
        assert "дружелюбно" in system_message["text"]
        assert "русском языке" in system_message["text"]

    def test_prepare_messages_context_limit(self, client, sample_context_data):
        """Тест ограничения контекста"""
        # Создаем большой контекст
        large_context = []
        for i in range(20):  # 20 пар = 40 сообщений
            large_context.extend([
                {"role": "user", "text": f"Сообщение {i}"},
                {"role": "assistant", "text": f"Ответ {i}"}
            ])
        
        client.chat_contexts[12345] = large_context
        
        messages = client._prepare_messages("Новое сообщение", 12345)
        
        # Должно быть системное сообщение + ограниченный контекст + новое сообщение
        # Контекст должен быть ограничен последними сообщениями
        assert len(messages) > 2
        assert messages[0]["role"] == "system"
        assert messages[-1]["role"] == "user"
        assert messages[-1]["text"] == "Новое сообщение"

    def test_get_response_with_context(self, client, sample_context_data, mock_yandex_response):
        """Тест получения ответа с контекстом"""
        with patch('services.yandex_client.requests.post') as mock_post:
            mock_post.return_value = mock_yandex_response
            
            # Устанавливаем контекст
            client.chat_contexts = sample_context_data
            
            response = client.get_response("Как дела?", 12345)
            
            assert response == "Тестовый ответ от Yandex GPT"
            
            # Проверяем что контекст был использован в запросе
            call_args = mock_post.call_args
            json_data = call_args[1]['json']
            messages = json_data['messages']
            
            # Должно быть системное сообщение + контекст + новое сообщение
            assert len(messages) >= 3
            assert messages[0]["role"] == "system"
            assert messages[-1]["role"] == "user"
            assert messages[-1]["text"] == "Как дела?"

    def test_get_response_context_update(self, client, mock_yandex_response):
        """Тест обновления контекста после получения ответа"""
        with patch('services.yandex_client.requests.post') as mock_post:
            mock_post.return_value = mock_yandex_response
            
            response = client.get_response("Привет", 12345)
            
            # Проверяем что контекст был обновлен
            assert 12345 in client.chat_contexts
            context = client.chat_contexts[12345]
            assert len(context) == 2
            assert context[0]["text"] == "Привет"
            assert context[1]["text"] == "Тестовый ответ от Yandex GPT"

    def test_client_with_iam_token_manager(self, mock_config):
        """Тест клиента с менеджером IAM токенов"""
        with patch('services.yandex_client.config') as mock_config:
            mock_config.YC_API_KEY = None
            mock_config.YC_IAM_TOKEN = None
            
            # Мокаем IAM токен менеджер
            with patch('services.yandex_client.token_manager') as mock_token_manager:
                mock_token_manager.get_token.return_value = 'test_iam_token'
                
                client = YandexClient()
                headers = client._get_headers()
                
                assert headers['Authorization'] == 'Bearer test_iam_token'

    def test_get_response_long_message(self, client, mock_yandex_response):
        """Тест обработки длинного сообщения"""
        with patch('services.yandex_client.requests.post') as mock_post:
            mock_post.return_value = mock_yandex_response
            
            long_message = "A" * 1000  # Длинное сообщение
            response = client.get_response(long_message, 12345)
            
            assert response == "Тестовый ответ от Yandex GPT"
            mock_post.assert_called_once()

    def test_get_response_unicode_message(self, client, mock_yandex_response):
        """Тест обработки Unicode сообщения"""
        with patch('services.yandex_client.requests.post') as mock_post:
            mock_post.return_value = mock_yandex_response
            
            unicode_message = "Привет, мир! 🌍 Тест с эмодзи 😊"
            response = client.get_response(unicode_message, 12345)
            
            assert response == "Тестовый ответ от Yandex GPT"
            
            # Проверяем что Unicode сообщение было передано в запросе
            call_args = mock_post.call_args
            json_data = call_args[1]['json']
            messages = json_data['messages']
            assert messages[-1]["text"] == unicode_message

