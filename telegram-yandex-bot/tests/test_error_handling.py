"""
Тесты для обработки ошибок в Telegram боте.
"""
import pytest
import sys
import os
from unittest.mock import patch, Mock, AsyncMock
import requests
from telegram.error import BadRequest, NetworkError, TimedOut

# Добавляем src в путь для импортов
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))


@pytest.mark.handlers
class TestErrorHandling:
    """Тесты для обработки ошибок"""

    @pytest.fixture
    def mock_context(self):
        """Фикстура для создания мока контекста"""
        context = Mock()
        context.bot = Mock()
        context.bot.send_message = AsyncMock()
        context.bot.send_chat_action = AsyncMock()
        context.bot.get_file = AsyncMock()
        return context

    def test_neuroapi_client_api_error(self, mock_config):
        """Тест обработки ошибки API NeuroAPI"""
        from services.neuroapi_client import NeuroAPIClient
        
        with patch('services.neuroapi_client.requests.post') as mock_post:
            # Мокаем ошибку API
            mock_response = Mock()
            mock_response.status_code = 429  # Too Many Requests
            mock_response.text = "Rate limit exceeded"
            mock_post.return_value = mock_response
            
            client = NeuroAPIClient()
            response = client.get_response("Тест", 12345)
            
            # Проверяем что ошибка обработана корректно
            assert "Извините, произошла ошибка" in response

    def test_neuroapi_client_network_error(self, mock_config):
        """Тест обработки сетевой ошибки NeuroAPI"""
        from services.neuroapi_client import NeuroAPIClient
        
        with patch('services.neuroapi_client.requests.post') as mock_post:
            # Мокаем сетевую ошибку
            mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")
            
            client = NeuroAPIClient()
            response = client.get_response("Тест", 12345)
            
            # Проверяем что ошибка обработана корректно
            assert "Произошла техническая ошибка" in response

    def test_neuroapi_client_timeout_error(self, mock_config):
        """Тест обработки таймаута NeuroAPI"""
        from services.neuroapi_client import NeuroAPIClient
        
        with patch('services.neuroapi_client.requests.post') as mock_post:
            # Мокаем таймаут
            mock_post.side_effect = requests.exceptions.Timeout("Request timeout")
            
            client = NeuroAPIClient()
            response = client.get_response("Тест", 12345)
            
            # Проверяем что таймаут обработан корректно
            assert "Превышено время ожидания" in response

    def test_neuroapi_client_invalid_response(self, mock_config):
        """Тест обработки невалидного ответа NeuroAPI"""
        from services.neuroapi_client import NeuroAPIClient
        
        with patch('services.neuroapi_client.requests.post') as mock_post:
            # Мокаем невалидный ответ
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"invalid": "response"}
            mock_post.return_value = mock_response
            
            client = NeuroAPIClient()
            response = client.get_response("Тест", 12345)
            
            # Проверяем что невалидный ответ обработан корректно
            assert "Извините, произошла ошибка" in response

    def test_speech_client_api_error(self, mock_config):
        """Тест обработки ошибки API Speech клиента"""
        from services.speech_client import SpeechClient
        
        with patch('services.speech_client.requests.post') as mock_post:
            # Мокаем ошибку API
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.text = "Bad Request"
            mock_post.return_value = mock_response
            
            client = SpeechClient()
            result = client.speech_to_text(b"fake_audio")
            
            # Проверяем что ошибка обработана корректно
            assert result is None

    def test_speech_client_network_error(self, mock_config):
        """Тест обработки сетевой ошибки Speech клиента"""
        from services.speech_client import SpeechClient
        
        with patch('services.speech_client.requests.post') as mock_post:
            # Мокаем сетевую ошибку
            mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")
            
            client = SpeechClient()
            result = client.speech_to_text(b"fake_audio")
            
            # Проверяем что ошибка обработана корректно
            assert result is None

    def test_iam_token_manager_error(self, mock_config):
        """Тест обработки ошибки IAM Token Manager"""
        from services.iam_token_manager import IamTokenManager
        
        with patch('services.iam_token_manager.requests.post') as mock_post:
            # Мокаем ошибку API
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.text = "Unauthorized"
            mock_post.return_value = mock_response
            
            manager = IamTokenManager()
            
            # Проверяем что ошибка обрабатывается корректно
            with pytest.raises(RuntimeError, match="Failed to obtain IAM token"):
                manager._request_iam_token()

    def test_iam_token_manager_invalid_key(self, mock_config):
        """Тест обработки невалидного ключа IAM Token Manager"""
        from services.iam_token_manager import IamTokenManager
        
        with patch('services.iam_token_manager.config') as mock_config:
            mock_config.YC_SA_KEY_JSON = "invalid json"
            
            manager = IamTokenManager()
            
            # Проверяем что невалидный ключ обрабатывается корректно
            with pytest.raises(ValueError, match="Invalid YC_SA_KEY_JSON"):
                manager._load_sa_key()

    @pytest.mark.asyncio
    async def test_command_handler_telegram_error(self, mock_update, mock_context):
        """Тест обработки ошибки Telegram в обработчике команд"""
        from handlers.commands import handle_text_message
        
        with patch('handlers.commands.get_gpt_response', return_value="Ответ") as mock_gpt, \
             patch('handlers.commands._send_typing_status', new_callable=AsyncMock), \
             patch('handlers.commands._reply_md_v2_safe', new_callable=AsyncMock) as mock_reply, \
             patch('handlers.commands.log_message'), \
             patch('handlers.commands.log_response') as mock_log_response:
            
            # Мокаем ошибку Telegram
            mock_reply.side_effect = BadRequest("Bad Request")
            
            # Мокаем fallback отправку сообщения
            mock_context.bot.send_message = AsyncMock()
            
            await handle_text_message(mock_update, mock_context)
            
            # Проверяем что ошибка была залогирована
            mock_log_response.assert_called()
            
            # Проверяем что fallback сообщение было отправлено
            mock_context.bot.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_command_handler_network_error(self, mock_update, mock_context):
        """Тест обработки сетевой ошибки в обработчике команд"""
        from handlers.commands import handle_text_message
        
        with patch('handlers.commands.get_gpt_response', side_effect=Exception("Network error")) as mock_gpt, \
             patch('handlers.commands._send_typing_status', new_callable=AsyncMock), \
             patch('handlers.commands.log_message'), \
             patch('handlers.commands.log_response') as mock_log_response:
            
            # Мокаем отправку сообщения об ошибке
            mock_context.bot.send_message = AsyncMock()
            
            await handle_text_message(mock_update, mock_context)
            
            # Проверяем что ошибка была залогирована
            mock_log_response.assert_called()
            
            # Проверяем что сообщение об ошибке было отправлено
            mock_context.bot.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_voice_handler_file_download_error(self, mock_voice_update, mock_context, mock_config):
        """Тест обработки ошибки загрузки файла в обработчике голоса"""
        from handlers.voice import handle_voice_message
        
        # Мокаем ошибку загрузки файла
        mock_context.bot.get_file.side_effect = Exception("Download error")
        
        with patch('handlers.voice._reply_md_v2_safe', new_callable=AsyncMock) as mock_reply, \
             patch('handlers.voice.log_message'), \
             patch('handlers.voice.log_response') as mock_log_response:
            
            await handle_voice_message(mock_voice_update, mock_context)
            
            # Проверяем что ошибка была залогирована
            mock_log_response.assert_called()
            
            # Проверяем что сообщение об ошибке было отправлено
            mock_reply.assert_called_once()
            error_text = mock_reply.call_args[0][2]
            assert "Произошла ошибка при обработке голосового сообщения" in error_text

    @pytest.mark.asyncio
    async def test_voice_handler_stt_error(self, mock_voice_update, mock_context, mock_config, mock_file_download):
        """Тест обработки ошибки STT в обработчике голоса"""
        from handlers.voice import handle_voice_message
        
        # Настраиваем моки
        mock_context.bot.get_file.return_value = mock_file_download
        mock_file_download.download_to_memory.return_value = None
        
        audio_data = b"fake_audio_data"
        with patch('handlers.voice.io.BytesIO') as mock_bytesio:
            mock_bytesio_instance = Mock()
            mock_bytesio_instance.getvalue.return_value = audio_data
            mock_bytesio.return_value = mock_bytesio_instance
            
            with patch('handlers.voice.speech_client.speech_to_text', return_value=None) as mock_stt, \
                 patch('handlers.voice._reply_md_v2_safe', new_callable=AsyncMock) as mock_reply, \
                 patch('handlers.voice.log_message'), \
                 patch('handlers.voice.log_response') as mock_log_response:
                
                await handle_voice_message(mock_voice_update, mock_context)
                
                # Проверяем что ошибка STT была обработана
                mock_stt.assert_called_once_with(audio_data)
                
                # Проверяем что было отправлено сообщение об ошибке распознавания
                assert mock_reply.call_count >= 2
                error_call = mock_reply.call_args_list[-1]
                error_text = error_call[0][2]
                assert "Не удалось распознать речь" in error_text

    @pytest.mark.asyncio
    async def test_voice_handler_tts_error(self, mock_voice_update, mock_context, mock_config, mock_file_download):
        """Тест обработки ошибки TTS в обработчике голоса"""
        from handlers.voice import handle_voice_message
        
        # Настраиваем моки
        mock_context.bot.get_file.return_value = mock_file_download
        mock_file_download.download_to_memory.return_value = None
        
        audio_data = b"fake_audio_data"
        with patch('handlers.voice.io.BytesIO') as mock_bytesio:
            mock_bytesio_instance = Mock()
            mock_bytesio_instance.getvalue.return_value = audio_data
            mock_bytesio.return_value = mock_bytesio_instance
            
            with patch('handlers.voice.speech_client.speech_to_text', return_value="Распознанный текст") as mock_stt, \
                 patch('handlers.voice.get_gpt_response', return_value="Ответ от GPT") as mock_gpt, \
                 patch('handlers.voice.speech_client.text_to_speech', return_value=None) as mock_tts, \
                 patch('handlers.voice._reply_md_v2_safe', new_callable=AsyncMock) as mock_reply, \
                 patch('handlers.voice.log_message'), \
                 patch('handlers.voice.log_response') as mock_log_response, \
                 patch('handlers.voice.config') as mock_config:
                
                mock_config.ENABLE_TTS_REPLY = True
                
                await handle_voice_message(mock_voice_update, mock_context)
                
                # Проверяем что TTS был вызван
                mock_tts.assert_called_once_with("Ответ от GPT")
                
                # Проверяем что голосовое сообщение НЕ было отправлено из-за ошибки TTS
                mock_voice_update.message.reply_voice.assert_not_called()
                
                # Проверяем логирование ошибки TTS
                assert mock_log_response.call_count >= 2

    def test_config_validation_error(self):
        """Тест обработки ошибки валидации конфигурации"""
        from config import Config
        
        # Тестируем с невалидными значениями
        with patch.dict(os.environ, {
            'NEUROAPI_TEMPERATURE': 'invalid_temperature',
            'NEUROAPI_MAX_TOKENS': 'not_a_number'
        }):
            with pytest.raises(ValueError):
                Config()

    def test_markdown_processing_error(self):
        """Тест обработки ошибки обработки Markdown"""
        from utils.markdown import transform_to_markdown_v2
        
        # Тестируем с None значением
        result = transform_to_markdown_v2(None)
        assert result == ""
        
        # Тестируем с пустой строкой
        result = transform_to_markdown_v2("")
        assert result == ""

    def test_logging_error_handling(self):
        """Тест обработки ошибок логирования"""
        from utils.logger import log_message, log_response
        
        # Тестируем логирование с None значениями
        log_message(
            chat_id=12345,
            user_id=67890,
            username=None,
            message_type="TEXT",
            content="Тест",
            message_id=None
        )
        
        # Тестируем логирование ответа с ошибкой
        log_response(12345, "TEXT", False, "Test error")
        
        # Если дошли сюда, значит ошибки обработаны корректно
        assert True

    def test_context_file_error_handling(self, temp_log_dir):
        """Тест обработки ошибок файла контекста"""
        from services.neuroapi_client import NeuroAPIClient
        
        # Создаем невалидный JSON файл
        invalid_json_file = os.path.join(temp_log_dir, "invalid_contexts.json")
        with open(invalid_json_file, 'w', encoding='utf-8') as f:
            f.write("invalid json content")
        
        with patch('services.neuroapi_client.os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data="invalid json content")):
            
            # Проверяем что ошибка обрабатывается корректно
            client = NeuroAPIClient()
            assert client.chat_contexts == {}  # Должен быть пустой словарь

    def test_webhook_handler_error(self):
        """Тест обработки ошибки webhook handler"""
        from bot import webhook_handler
        
        # Создаем мок запроса с ошибкой
        mock_request = Mock()
        mock_request.json = AsyncMock(side_effect=Exception("JSON error"))
        
        with patch('bot.log_error') as mock_log_error:
            import asyncio
            response = asyncio.run(webhook_handler(mock_request))
            
            # Проверяем что ошибка была залогирована
            mock_log_error.assert_called_once()
            
            # Проверяем ответ об ошибке
            assert response.status == 500
            assert response.text == "Error"

    def test_application_not_initialized_error(self):
        """Тест обработки ошибки неинициализированного application"""
        from bot import webhook_handler
        
        # Создаем мок запроса
        mock_request = Mock()
        mock_request.json = AsyncMock(return_value={"update_id": 1})
        
        with patch('bot.application', None), \
             patch('bot.log_error') as mock_log_error:
            
            import asyncio
            response = asyncio.run(webhook_handler(mock_request))
            
            # Проверяем что ошибка была залогирована
            mock_log_error.assert_called_once_with("Application not initialized")
            
            # Проверяем ответ об ошибке
            assert response.status == 500
            assert response.text == "Application not initialized"

    def test_retry_logic_neuroapi(self, mock_config):
        """Тест логики повторных попыток NeuroAPI"""
        from services.neuroapi_client import NeuroAPIClient
        
        with patch('services.neuroapi_client.requests.post') as mock_post:
            # Первый ответ пустой, второй успешный
            empty_response = Mock()
            empty_response.status_code = 200
            empty_response.json.return_value = {
                "choices": [{
                    "message": {
                        "content": ""  # Пустой ответ
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
            
            client = NeuroAPIClient()
            response = client.get_response("Тест", 12345)
            
            # Проверяем что был выполнен повторный запрос
            assert mock_post.call_count == 2
            assert response == "Успешный ответ"

    def test_fallback_responses(self, mock_config):
        """Тест fallback ответов при ошибках"""
        from services.neuroapi_client import NeuroAPIClient
        
        with patch('services.neuroapi_client.requests.post') as mock_post:
            # Мокаем ошибку API
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_post.return_value = mock_response
            
            client = NeuroAPIClient()
            
            # Тестируем обычное сообщение
            response = client.get_response("Тест", 12345)
            assert "Извините, произошла ошибка" in response
            
            # Тестируем бизнес-сообщение
            response = client.get_response("Тест", 12345, is_business_message=True, business_connection_id="test")
            assert "ИИ-ассистент Сергея" in response

