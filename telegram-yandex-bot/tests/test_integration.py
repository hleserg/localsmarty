"""
Интеграционные тесты для Telegram бота.
Тестируют взаимодействие между различными компонентами системы.
"""
import pytest
import sys
import os
import json
import tempfile
from unittest.mock import patch, Mock, AsyncMock, mock_open
from datetime import datetime

# Добавляем src в путь для импортов
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from services.neuroapi_client import NeuroAPIClient
from services.speech_client import SpeechClient
from services.iam_token_manager import IamTokenManager
from handlers.commands import handle_text_message, handle_business_message
from handlers.voice import handle_voice_message


@pytest.mark.integration
class TestIntegration:
    """Интеграционные тесты"""

    @pytest.fixture
    def mock_context(self):
        """Фикстура для создания мока контекста"""
        context = Mock()
        context.bot = Mock()
        context.bot.send_message = AsyncMock()
        context.bot.send_chat_action = AsyncMock()
        context.bot.get_file = AsyncMock()
        return context

    def test_neuroapi_client_with_context_persistence(self, temp_log_dir, sample_context_data):
        """Тест интеграции NeuroAPI клиента с персистентностью контекста"""
        # Создаем временный файл контекста
        context_file = os.path.join(temp_log_dir, "test_contexts.json")
        with open(context_file, 'w', encoding='utf-8') as f:
            json.dump(sample_context_data, f, ensure_ascii=False, indent=2)
        
        with patch('services.neuroapi_client.os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=json.dumps(sample_context_data, ensure_ascii=False))), \
             patch('services.neuroapi_client.requests.post') as mock_post:
            
            # Мокаем успешный ответ от NeuroAPI
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{
                    "message": {
                        "content": "Ответ с учетом контекста"
                    }
                }]
            }
            mock_post.return_value = mock_response
            
            # Создаем клиента
            client = NeuroAPIClient()
            client.context_file = context_file
            
            # Тестируем получение ответа с контекстом
            response = client.get_response("Как дела?", 12345)
            
            assert response == "Ответ с учетом контекста"
            
            # Проверяем что контекст был обновлен
            assert 12345 in client.chat_contexts
            context = client.chat_contexts[12345]
            assert len(context) >= 2  # Должен содержать новую пару сообщений

    def test_speech_client_with_iam_token_manager(self, mock_config):
        """Тест интеграции Speech клиента с IAM Token Manager"""
        with patch('services.speech_client.config') as mock_config:
            mock_config.YC_API_KEY = None
            mock_config.YC_IAM_TOKEN = None
            mock_config.ENABLE_VOICE = True
            
            # Мокаем IAM токен менеджер
            with patch('services.speech_client.token_manager') as mock_token_manager:
                mock_token_manager.get_token.return_value = 'test_iam_token'
                
                # Мокаем успешный ответ от Speech API
                with patch('services.speech_client.requests.post') as mock_post:
                    mock_response = Mock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = {"result": "Распознанный текст"}
                    mock_post.return_value = mock_response
                    
                    # Создаем клиента
                    client = SpeechClient()
                    
                    # Тестируем STT
                    result = client.speech_to_text(b"fake_audio")
                    
                    assert result == "Распознанный текст"
                    
                    # Проверяем что IAM токен был использован
                    call_args = mock_post.call_args
                    headers = call_args[1]['headers']
                    assert headers['Authorization'] == 'Bearer test_iam_token'

    def test_business_message_flow(self, mock_business_update, mock_context, mock_config):
        """Тест полного потока обработки бизнес-сообщения"""
        with patch('handlers.commands.get_gpt_response', return_value="Бизнес ответ") as mock_gpt, \
             patch('handlers.commands._send_business_typing_status', new_callable=AsyncMock) as mock_typing, \
             patch('handlers.commands._reply_business_md_v2_safe', new_callable=AsyncMock) as mock_reply, \
             patch('handlers.commands.log_message') as mock_log_message, \
             patch('handlers.commands.log_response') as mock_log_response:
            
            # Выполняем обработку бизнес-сообщения
            import asyncio
            asyncio.run(handle_business_message(mock_business_update, mock_context))
            
            # Проверяем весь поток
            mock_typing.assert_called_once()
            mock_gpt.assert_called_once_with(
                "Тестовое бизнес-сообщение", 
                67890, 
                is_business_message=True, 
                business_connection_id="test_business_connection_id"
            )
            mock_reply.assert_called_once()
            mock_log_message.assert_called_once()
            mock_log_response.assert_called_once()

    def test_voice_message_flow(self, mock_voice_update, mock_context, mock_config, mock_file_download):
        """Тест полного потока обработки голосового сообщения"""
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
                 patch('handlers.voice._reply_md_v2_safe', new_callable=AsyncMock) as mock_reply, \
                 patch('handlers.voice.log_message') as mock_log_message, \
                 patch('handlers.voice.log_response') as mock_log_response:
                
                # Выполняем обработку голосового сообщения
                import asyncio
                asyncio.run(handle_voice_message(mock_voice_update, mock_context))
                
                # Проверяем весь поток
                mock_stt.assert_called_once_with(audio_data)
                mock_gpt.assert_called_once_with("Распознанный текст", 67890)
                assert mock_reply.call_count >= 2  # Сообщение о обработке + распознанный текст + ответ GPT
                mock_log_message.assert_called_once()
                assert mock_log_response.call_count >= 2

    def test_context_management_across_messages(self, temp_log_dir):
        """Тест управления контекстом между сообщениями"""
        context_file = os.path.join(temp_log_dir, "test_contexts.json")
        
        with patch('services.neuroapi_client.os.path.exists', return_value=False), \
             patch('services.neuroapi_client.requests.post') as mock_post:
            
            # Мокаем ответы от NeuroAPI
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{
                    "message": {
                        "content": "Ответ на сообщение"
                    }
                }]
            }
            mock_post.return_value = mock_response
            
            # Создаем клиента
            client = NeuroAPIClient()
            client.context_file = context_file
            
            # Отправляем несколько сообщений
            client.get_response("Привет", 12345)
            client.get_response("Как дела?", 12345)
            client.get_response("Что нового?", 12345)
            
            # Проверяем что контекст накапливается
            assert 12345 in client.chat_contexts
            context = client.chat_contexts[12345]
            assert len(context) == 6  # 3 пары сообщений

    def test_business_context_isolation(self, temp_log_dir):
        """Тест изоляции контекста между обычными и бизнес-сообщениями"""
        with patch('services.neuroapi_client.os.path.exists', return_value=False), \
             patch('services.neuroapi_client.requests.post') as mock_post:
            
            # Мокаем ответы от NeuroAPI
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{
                    "message": {
                        "content": "Ответ"
                    }
                }]
            }
            mock_post.return_value = mock_response
            
            # Создаем клиента
            client = NeuroAPIClient()
            
            # Отправляем обычное сообщение
            client.get_response("Обычное сообщение", 12345)
            
            # Отправляем бизнес-сообщение
            client.get_response("Бизнес сообщение", 12345, is_business_message=True, business_connection_id="test_connection")
            
            # Проверяем что контексты изолированы
            assert 12345 in client.chat_contexts
            assert "business_test_connection_12345" in client.chat_contexts
            
            # Контексты должны быть независимыми
            regular_context = client.chat_contexts[12345]
            business_context = client.chat_contexts["business_test_connection_12345"]
            
            assert len(regular_context) == 2  # Одно сообщение
            assert len(business_context) == 2  # Одно сообщение

    def test_error_handling_integration(self, mock_update, mock_context):
        """Тест интеграции обработки ошибок"""
        with patch('handlers.commands.get_gpt_response', side_effect=Exception("API Error")) as mock_gpt, \
             patch('handlers.commands._send_typing_status', new_callable=AsyncMock), \
             patch('handlers.commands.log_message'), \
             patch('handlers.commands.log_response') as mock_log_response:
            
            # Мокаем отправку сообщения об ошибке
            mock_context.bot.send_message = AsyncMock()
            
            # Выполняем обработку сообщения с ошибкой
            import asyncio
            asyncio.run(handle_text_message(mock_update, mock_context))
            
            # Проверяем что ошибка была обработана
            mock_log_response.assert_called()
            mock_context.bot.send_message.assert_called_once()

    def test_config_integration_across_services(self, mock_config):
        """Тест интеграции конфигурации между сервисами"""
        with patch('services.neuroapi_client.config') as neuroapi_config, \
             patch('services.speech_client.config') as speech_config, \
             patch('services.iam_token_manager.config') as iam_config:
            
            # Устанавливаем одинаковую конфигурацию для всех сервисов
            for config_mock in [neuroapi_config, speech_config, iam_config]:
                config_mock.NEUROAPI_API_KEY = 'test_key'
                config_mock.ENABLE_VOICE = True
                config_mock.ENABLE_CONTEXT = True
            
            # Создаем сервисы
            neuroapi_client = NeuroAPIClient()
            speech_client = SpeechClient()
            iam_manager = IamTokenManager()
            
            # Проверяем что конфигурация применяется корректно
            assert neuroapi_client.api_key == 'test_key'
            assert speech_client.api_key == 'test_yc_key'  # Speech использует YC ключ

    def test_logging_integration(self, mock_update, mock_context):
        """Тест интеграции логирования"""
        with patch('handlers.commands.get_gpt_response', return_value="Тестовый ответ") as mock_gpt, \
             patch('handlers.commands._send_typing_status', new_callable=AsyncMock), \
             patch('handlers.commands._reply_md_v2_safe', new_callable=AsyncMock), \
             patch('handlers.commands.log_message') as mock_log_message, \
             patch('handlers.commands.log_response') as mock_log_response:
            
            # Выполняем обработку сообщения
            import asyncio
            asyncio.run(handle_text_message(mock_update, mock_context))
            
            # Проверяем что логирование работает корректно
            mock_log_message.assert_called_once()
            mock_log_response.assert_called_once()
            
            # Проверяем параметры логирования
            log_message_call = mock_log_message.call_args
            assert log_message_call[1]['chat_id'] == 67890
            assert log_message_call[1]['user_id'] == 12345
            assert log_message_call[1]['message_type'] == "TEXT"
            assert log_message_call[1]['content'] == "Тестовое сообщение"

    def test_webhook_handler_integration(self):
        """Тест интеграции webhook обработчика (без реального webhook)"""
        from bot import webhook_handler
        
        # Создаем мок запроса
        mock_request = Mock()
        mock_request.json = AsyncMock(return_value={
            "update_id": 1,
            "message": {
                "message_id": 1,
                "text": "Тестовое сообщение",
                "from": {
                    "id": 12345,
                    "username": "testuser",
                    "first_name": "Test"
                },
                "chat": {
                    "id": 67890,
                    "type": "private"
                }
            }
        })
        
        with patch('bot.application') as mock_app:
            mock_app.process_update = AsyncMock()
            
            # Выполняем обработку webhook
            import asyncio
            response = asyncio.run(webhook_handler(mock_request))
            
            # Проверяем что update был обработан
            mock_app.process_update.assert_called_once()
            assert response.status == 200
            assert response.text == "OK"

    def test_health_check_integration(self):
        """Тест интеграции health check"""
        from bot import health_handler
        
        # Создаем мок запроса
        mock_request = Mock()
        
        # Выполняем health check
        import asyncio
        response = asyncio.run(health_handler(mock_request))
        
        # Проверяем ответ
        assert response.status == 200
        assert response.text == "OK"

    def test_status_endpoint_integration(self, mock_config):
        """Тест интеграции status endpoint"""
        from bot import status_handler
        
        # Создаем мок запроса
        mock_request = Mock()
        
        # Выполняем status check
        import asyncio
        response = asyncio.run(status_handler(mock_request))
        
        # Проверяем ответ
        assert response.status == 200
        status_data = response.body
        assert "status" in status_data
        assert "webhook_url" in status_data
        assert "port" in status_data
        assert "voice_enabled" in status_data
        assert "context_enabled" in status_data

    def test_markdown_integration(self):
        """Тест интеграции с markdown утилитами"""
        from utils.markdown import transform_to_markdown_v2
        from handlers.commands import _reply_md_v2_safe
        
        # Тестируем что markdown утилиты работают с обработчиками
        test_text = "**Привет!** Это тестовое сообщение с __форматированием__."
        formatted_text = transform_to_markdown_v2(test_text)
        
        assert "*Привет\\!*" in formatted_text
        assert "_форматированием_" in formatted_text

    def test_models_integration(self):
        """Тест интеграции с моделями данных"""
        from models.messages import UserMessage, BotResponse, ErrorMessage
        
        # Тестируем создание моделей
        user_msg = UserMessage(user_id="123", text="Тест")
        bot_resp = BotResponse(response_text="Ответ", is_typing=True)
        error_msg = ErrorMessage(error="Ошибка", code=500)
        
        assert user_msg.user_id == "123"
        assert user_msg.text == "Тест"
        assert bot_resp.response_text == "Ответ"
        assert bot_resp.is_typing is True
        assert error_msg.error == "Ошибка"
        assert error_msg.code == 500

