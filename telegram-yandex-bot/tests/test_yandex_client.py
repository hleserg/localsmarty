import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Добавляем src директорию в путь для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.yandex_client import YandexClient, get_gpt_response

class TestYandexClient(unittest.TestCase):

    def setUp(self):
        # Настройка переменных окружения для тестов
        os.environ['YANDEX_API_KEY'] = 'test-api-key'
        os.environ['YANDEX_FOLDER_ID'] = 'test-folder-id'
        os.environ['YANDEX_MODEL'] = 'yandexgpt-lite/latest'
        
        self.client = YandexClient()

    @patch('requests.post')
    def test_get_response_success(self, mock_post):
        """Тест успешного получения ответа от YandexGPT"""
        # Настройка мока
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'result': {
                'alternatives': [
                    {
                        'message': {
                            'text': 'Тестовый ответ от YandexGPT'
                        }
                    }
                ]
            }
        }
        mock_post.return_value = mock_response

        # Тестирование
        user_input = "Привет, как дела?"
        response = self.client.get_response(user_input)
        
        # Проверки
        self.assertEqual(response, 'Тестовый ответ от YandexGPT')
        mock_post.assert_called_once()
        
        # Проверяем правильность параметров запроса
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]['headers']['Authorization'], 'Api-Key test-api-key')
        self.assertEqual(call_args[1]['json']['modelUri'], 'gpt://test-folder-id/yandexgpt-lite/latest')

    @patch('requests.post')
    def test_get_response_api_error(self, mock_post):
        """Тест обработки ошибки API"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = 'Bad Request'
        mock_post.return_value = mock_response

        user_input = "Тест ошибки"
        response = self.client.get_response(user_input)
        
        self.assertIn("Ошибка при обращении к AI", response)

    @patch('requests.post')
    def test_get_response_timeout(self, mock_post):
        """Тест обработки таймаута"""
        import requests
        mock_post.side_effect = requests.exceptions.Timeout()

        user_input = "Тест таймаута"
        response = self.client.get_response(user_input)
        
        self.assertIn("превышено время ожидания", response)

    @patch('services.yandex_client._get_client')
    def test_get_gpt_response_function(self, mock_get_client):
        """Тест функции-обертки get_gpt_response"""
        # Настройка мока
        mock_client = MagicMock()
        mock_client.get_response.return_value = 'Ответ от функции'
        mock_get_client.return_value = mock_client
        
        response = get_gpt_response("Тестовое сообщение")
        self.assertEqual(response, 'Ответ от функции')

    def test_missing_api_key(self):
        """Тест ошибки при отсутствии API ключа"""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                YandexClient()

    def test_missing_folder_id(self):
        """Тест ошибки при отсутствии folder_id"""
        with patch.dict(os.environ, {'YANDEX_API_KEY': 'test-key'}, clear=True):
            with self.assertRaises(ValueError):
                YandexClient()

if __name__ == '__main__':
    unittest.main()