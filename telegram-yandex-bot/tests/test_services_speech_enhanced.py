"""
Расширенные тесты для сервиса Speech клиента.
"""
import pytest
import sys
import os
from unittest.mock import patch, Mock

# Добавляем src в путь для импортов
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from services.speech_client import SpeechClient


@pytest.mark.services
class TestSpeechClientEnhanced:
    """Расширенные тесты для Speech клиента"""

    @pytest.fixture
    def client(self, mock_config):
        """Фикстура для создания клиента Speech"""
        return SpeechClient()

    def test_client_initialization(self, client):
        """Тест инициализации клиента"""
        assert client.api_key == 'test_yc_key'
        assert client.folder_id == 'test_folder'
        assert client.stt_endpoint == 'https://test.endpoint/stt'
        assert client.tts_endpoint == 'https://test.endpoint/tts'
        assert client.stt_language == 'ru-RU'
        assert client.tts_voice == 'alena'
        assert client.tts_format == 'oggopus'

    def test_get_headers_with_api_key(self, client):
        """Тест получения заголовков с API ключом"""
        headers = client._get_headers()
        
        expected_headers = {
            "Authorization": "Api-Key test_yc_key"
        }
        assert headers == expected_headers

    def test_get_headers_with_iam_token(self, client):
        """Тест получения заголовков с IAM токеном"""
        with patch('services.speech_client.config') as mock_config:
            mock_config.YC_API_KEY = None
            mock_config.YC_IAM_TOKEN = 'test_iam_token'
            
            headers = client._get_headers()
            
            expected_headers = {
                "Authorization": "Bearer test_iam_token"
            }
            assert headers == expected_headers

    def test_get_headers_no_credentials(self, client):
        """Тест получения заголовков без учетных данных"""
        with patch('services.speech_client.config') as mock_config:
            mock_config.YC_API_KEY = None
            mock_config.YC_IAM_TOKEN = None
            
            with pytest.raises(ValueError, match="No API key or IAM token provided"):
                client._get_headers()

    @patch('services.speech_client.requests.post')
    def test_speech_to_text_success(self, mock_post, client, mock_speech_response):
        """Тест успешного преобразования речи в текст"""
        mock_post.return_value = mock_speech_response
        
        audio_data = b"fake_audio_data"
        result = client.speech_to_text(audio_data)
        
        assert result == "Распознанный текст"
        mock_post.assert_called_once()

    @patch('services.speech_client.requests.post')
    def test_speech_to_text_api_error(self, mock_post, client):
        """Тест обработки ошибки API при преобразовании речи"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response
        
        audio_data = b"fake_audio_data"
        result = client.speech_to_text(audio_data)
        
        assert result is None

    @patch('services.speech_client.requests.post')
    def test_speech_to_text_network_error(self, mock_post, client):
        """Тест обработки сетевой ошибки при преобразовании речи"""
        mock_post.side_effect = Exception("Network error")
        
        audio_data = b"fake_audio_data"
        result = client.speech_to_text(audio_data)
        
        assert result is None

    @patch('services.speech_client.requests.post')
    def test_speech_to_text_invalid_response(self, mock_post, client):
        """Тест обработки невалидного ответа при преобразовании речи"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"invalid": "response"}
        mock_post.return_value = mock_response
        
        audio_data = b"fake_audio_data"
        result = client.speech_to_text(audio_data)
        
        assert result is None

    @patch('services.speech_client.requests.post')
    def test_text_to_speech_success(self, mock_post, client, mock_speech_response):
        """Тест успешного преобразования текста в речь"""
        mock_post.return_value = mock_speech_response
        
        text = "Тестовый текст"
        result = client.text_to_speech(text)
        
        assert result == b"fake_audio_data"
        mock_post.assert_called_once()

    @patch('services.speech_client.requests.post')
    def test_text_to_speech_api_error(self, mock_post, client):
        """Тест обработки ошибки API при преобразовании текста"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response
        
        text = "Тестовый текст"
        result = client.text_to_speech(text)
        
        assert result is None

    @patch('services.speech_client.requests.post')
    def test_text_to_speech_network_error(self, mock_post, client):
        """Тест обработки сетевой ошибки при преобразовании текста"""
        mock_post.side_effect = Exception("Network error")
        
        text = "Тестовый текст"
        result = client.text_to_speech(text)
        
        assert result is None

    def test_voice_disabled_stt(self, client):
        """Тест поведения STT когда голос отключен"""
        with patch('services.speech_client.config') as mock_config:
            mock_config.ENABLE_VOICE = False
            
            audio_data = b"fake_audio_data"
            result = client.speech_to_text(audio_data)
            
            assert result is None

    def test_voice_disabled_tts(self, client):
        """Тест поведения TTS когда голос отключен"""
        with patch('services.speech_client.config') as mock_config:
            mock_config.ENABLE_VOICE = False
            
            text = "Тестовый текст"
            result = client.text_to_speech(text)
            
            assert result is None

    @patch('services.speech_client.requests.post')
    def test_speech_to_text_request_params(self, mock_post, client, mock_speech_response):
        """Тест параметров запроса для STT"""
        mock_post.return_value = mock_speech_response
        
        audio_data = b"fake_audio_data"
        client.speech_to_text(audio_data)
        
        # Проверяем параметры запроса
        call_args = mock_post.call_args
        assert call_args[0][0] == client.stt_endpoint
        
        # Проверяем заголовки
        headers = call_args[1]['headers']
        assert 'Authorization' in headers
        
        # Проверяем данные
        data = call_args[1]['data']
        assert 'audio' in data.fields
        assert 'language' in data.fields
        assert 'format' in data.fields

    @patch('services.speech_client.requests.post')
    def test_text_to_speech_request_params(self, mock_post, client, mock_speech_response):
        """Тест параметров запроса для TTS"""
        mock_post.return_value = mock_speech_response
        
        text = "Тестовый текст"
        client.text_to_speech(text)
        
        # Проверяем параметры запроса
        call_args = mock_post.call_args
        assert call_args[0][0] == client.tts_endpoint
        
        # Проверяем заголовки
        headers = call_args[1]['headers']
        assert 'Authorization' in headers
        
        # Проверяем данные
        data = call_args[1]['data']
        assert 'text' in data.fields
        assert 'voice' in data.fields
        assert 'format' in data.fields

    def test_speech_to_text_empty_audio(self, client):
        """Тест обработки пустого аудио"""
        result = client.speech_to_text(b"")
        assert result is None

    def test_text_to_speech_empty_text(self, client):
        """Тест обработки пустого текста"""
        result = client.text_to_speech("")
        assert result is None

    def test_text_to_speech_none_text(self, client):
        """Тест обработки None текста"""
        result = client.text_to_speech(None)
        assert result is None

    @patch('services.speech_client.requests.post')
    def test_speech_to_text_different_language(self, mock_post, client, mock_speech_response):
        """Тест STT с другим языком"""
        mock_post.return_value = mock_speech_response
        
        with patch('services.speech_client.config') as mock_config:
            mock_config.STT_LANGUAGE = 'en-US'
            
            audio_data = b"fake_audio_data"
            client.speech_to_text(audio_data)
            
            # Проверяем что язык был передан в запросе
            call_args = mock_post.call_args
            data = call_args[1]['data']
            assert data.fields['language'] == 'en-US'

    @patch('services.speech_client.requests.post')
    def test_text_to_speech_different_voice(self, mock_post, client, mock_speech_response):
        """Тест TTS с другим голосом"""
        mock_post.return_value = mock_speech_response
        
        with patch('services.speech_client.config') as mock_config:
            mock_config.TTS_VOICE = 'john'
            
            text = "Тестовый текст"
            client.text_to_speech(text)
            
            # Проверяем что голос был передан в запросе
            call_args = mock_post.call_args
            data = call_args[1]['data']
            assert data.fields['voice'] == 'john'

    @patch('services.speech_client.requests.post')
    def test_text_to_speech_different_format(self, mock_post, client, mock_speech_response):
        """Тест TTS с другим форматом"""
        mock_post.return_value = mock_speech_response
        
        with patch('services.speech_client.config') as mock_config:
            mock_config.TTS_FORMAT = 'mp3'
            
            text = "Тестовый текст"
            client.text_to_speech(text)
            
            # Проверяем что формат был передан в запросе
            call_args = mock_post.call_args
            data = call_args[1]['data']
            assert data.fields['format'] == 'mp3'

    @patch('services.speech_client.requests.post')
    def test_speech_to_text_large_audio(self, mock_post, client, mock_speech_response):
        """Тест STT с большим аудио файлом"""
        mock_post.return_value = mock_speech_response
        
        large_audio = b"fake_audio_data" * 1000  # Большой файл
        result = client.speech_to_text(large_audio)
        
        assert result == "Распознанный текст"
        mock_post.assert_called_once()

    @patch('services.speech_client.requests.post')
    def test_text_to_speech_long_text(self, mock_post, client, mock_speech_response):
        """Тест TTS с длинным текстом"""
        mock_post.return_value = mock_speech_response
        
        long_text = "Это очень длинный текст " * 100
        result = client.text_to_speech(long_text)
        
        assert result == b"fake_audio_data"
        mock_post.assert_called_once()

    def test_client_with_iam_token_manager(self, mock_config):
        """Тест клиента с менеджером IAM токенов"""
        with patch('services.speech_client.config') as mock_config:
            mock_config.YC_API_KEY = None
            mock_config.YC_IAM_TOKEN = None
            
            # Мокаем IAM токен менеджер
            with patch('services.speech_client.token_manager') as mock_token_manager:
                mock_token_manager.get_token.return_value = 'test_iam_token'
                
                client = SpeechClient()
                headers = client._get_headers()
                
                assert headers['Authorization'] == 'Bearer test_iam_token'

    def test_speech_to_text_unicode_text(self, client, mock_speech_response):
        """Тест STT с Unicode текстом в ответе"""
        with patch('services.speech_client.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "result": "Привет, мир! 🌍"
            }
            mock_post.return_value = mock_response
            
            audio_data = b"fake_audio_data"
            result = client.speech_to_text(audio_data)
            
            assert result == "Привет, мир! 🌍"

    def test_text_to_speech_unicode_text(self, client, mock_speech_response):
        """Тест TTS с Unicode текстом"""
        with patch('services.speech_client.requests.post') as mock_post:
            mock_post.return_value = mock_speech_response
            
            unicode_text = "Привет, мир! 🌍"
            result = client.text_to_speech(unicode_text)
            
            assert result == b"fake_audio_data"
            
            # Проверяем что Unicode текст был передан в запросе
            call_args = mock_post.call_args
            data = call_args[1]['data']
            assert data.fields['text'] == unicode_text

