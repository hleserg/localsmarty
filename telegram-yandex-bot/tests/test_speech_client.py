import unittest
from unittest.mock import patch, Mock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

class TestSpeechClient(unittest.TestCase):

    @patch('services.speech_client.config')
    def setUp(self, mock_config):
        # Mock configuration for testing
        mock_config.YC_API_KEY = "test_api_key"
        mock_config.YC_IAM_TOKEN = None
        mock_config.YC_FOLDER_ID = "test_folder"
        mock_config.YC_STT_ENDPOINT = "https://test.endpoint/stt"
        mock_config.YC_TTS_ENDPOINT = "https://test.endpoint/tts"
        mock_config.ENABLE_VOICE = True
        mock_config.STT_LANGUAGE = "ru-RU"
        mock_config.TTS_VOICE = "alena"
        mock_config.TTS_FORMAT = "oggopus"
        
        from services.speech_client import SpeechClient
        self.client = SpeechClient()

    @patch('services.speech_client.requests.post')
    @patch('services.speech_client.config')
    def test_speech_to_text_success(self, mock_config, mock_post):
        """Test successful speech-to-text conversion"""
        # Setup config mock
        mock_config.ENABLE_VOICE = True
        mock_config.STT_LANGUAGE = "ru-RU"
        mock_config.YC_FOLDER_ID = "test_folder"
        
        audio_data = b"fake_audio_data"
        
        # Mock the API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": "Привет, как дела?"
        }
        mock_post.return_value = mock_response
        
        result = self.client.speech_to_text(audio_data)
        self.assertEqual(result, "Привет, как дела?")

    @patch('services.speech_client.requests.post')
    @patch('services.speech_client.config')
    def test_speech_to_text_error(self, mock_config, mock_post):
        """Test handling of STT API errors"""
        # Setup config mock
        mock_config.ENABLE_VOICE = True
        
        audio_data = b"fake_audio_data"
        
        # Mock API error response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response
        
        result = self.client.speech_to_text(audio_data)
        self.assertIsNone(result)

    @patch('services.speech_client.requests.post')
    @patch('services.speech_client.config')
    def test_text_to_speech_success(self, mock_config, mock_post):
        """Test successful text-to-speech conversion"""
        # Setup config mock
        mock_config.ENABLE_VOICE = True
        mock_config.TTS_VOICE = "alena"
        mock_config.TTS_FORMAT = "oggopus"
        mock_config.YC_FOLDER_ID = "test_folder"
        
        text = "Привет, как дела?"
        
        # Mock the API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"fake_audio_data"
        mock_post.return_value = mock_response
        
        result = self.client.text_to_speech(text)
        self.assertEqual(result, b"fake_audio_data")

    @patch('services.speech_client.requests.post')
    @patch('services.speech_client.config')
    def test_text_to_speech_error(self, mock_config, mock_post):
        """Test handling of TTS API errors"""
        # Setup config mock
        mock_config.ENABLE_VOICE = True
        
        text = "Привет, как дела?"
        
        # Mock API error response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response
        
        result = self.client.text_to_speech(text)
        self.assertIsNone(result)

    @patch('services.speech_client.config')
    def test_voice_disabled(self, mock_config):
        """Test behavior when voice is disabled"""
        mock_config.ENABLE_VOICE = False
        
        result_stt = self.client.speech_to_text(b"fake_audio")
        result_tts = self.client.text_to_speech("test text")
        
        self.assertIsNone(result_stt)
        self.assertIsNone(result_tts)

if __name__ == '__main__':
    unittest.main()