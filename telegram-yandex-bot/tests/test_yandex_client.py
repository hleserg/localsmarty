import unittest
from unittest.mock import patch, Mock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from services.yandex_client import YandexClient

class TestYandexClient(unittest.TestCase):

    def setUp(self):
        # Mock configuration for testing
        with patch('services.yandex_client.config') as mock_config:
            mock_config.YC_API_KEY = "test_api_key"
            mock_config.YC_IAM_TOKEN = None
            mock_config.YC_FOLDER_ID = "test_folder"
            mock_config.YC_MODEL_URI = "gpt://test_folder/yandexgpt/latest"
            mock_config.YC_FOUNDATION_MODELS_ENDPOINT = "https://test.endpoint/chat/completion"
            mock_config.YC_TEMPERATURE = 0.3
            mock_config.YC_MAX_TOKENS = 800
            mock_config.ENABLE_CONTEXT = True
            self.client = YandexClient()

    def test_get_response_success(self):
        """Test successful response from Yandex GPT"""
        user_input = "Привет, как дела?"
        
        # Mock the API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {
                "alternatives": [{
                    "message": {
                        "text": "Привет! Дела хорошо, спасибо!"
                    }
                }]
            }
        }
        
        with patch('services.yandex_client.requests.post', return_value=mock_response):
            response = self.client.get_response(user_input, chat_id=123)
            
        self.assertIsInstance(response, str)
        self.assertEqual(response, "Привет! Дела хорошо, спасибо!")

    def test_empty_input(self):
        """Test handling of empty input"""
        user_input = ""
        response = self.client.get_response(user_input, chat_id=123)
        self.assertEqual(response, "Ошибка: пустой ввод")

    def test_api_error(self):
        """Test handling of API errors"""
        user_input = "Тестовое сообщение"
        
        # Mock API error response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        
        with patch('services.yandex_client.requests.post', return_value=mock_response):
            response = self.client.get_response(user_input, chat_id=123)
            
        self.assertIn("Извините, произошла ошибка", response)

    def test_context_management(self):
        """Test context management functionality"""
        chat_id = 123
        
        # First message
        self.client._update_context(chat_id, "Привет", "Привет! Как дела?")
        
        # Check context is stored
        self.assertIn(chat_id, self.client.chat_contexts)
        self.assertEqual(len(self.client.chat_contexts[chat_id]), 2)
        
        # Prepare messages with context
        messages = self.client._prepare_messages("Хорошо", chat_id)
        
        # Should include system message, previous context, and new message
        self.assertGreater(len(messages), 2)
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[-1]["text"], "Хорошо")

if __name__ == '__main__':
    unittest.main()