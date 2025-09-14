"""
Тесты для модуля утилит логгера.
"""
import pytest
import sys
import os
import tempfile
import json
from datetime import datetime
from unittest.mock import patch, mock_open, call
from io import StringIO

# Добавляем src в путь для импортов
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from utils.logger import log_info, log_error, log_message, log_response, log_update_json


@pytest.mark.utils
class TestLoggerUtils:
    """Тесты для утилит логирования"""

    def test_log_info_basic(self):
        """Тест базового логирования информации"""
        with patch('utils.logger.logger') as mock_logger:
            log_info("Test info message")
            mock_logger.info.assert_called_once_with("Test info message")

    def test_log_error_basic(self):
        """Тест базового логирования ошибок"""
        with patch('utils.logger.logger') as mock_logger:
            log_error("Test error message")
            mock_logger.error.assert_called_once_with("Test error message")

    def test_log_message_basic(self):
        """Тест логирования сообщения с базовыми параметрами"""
        with patch('utils.logger.logger') as mock_logger, \
             patch('utils.logger.print') as mock_print:
            
            log_message(
                chat_id=12345,
                user_id=67890,
                username="testuser",
                message_type="TEXT",
                content="Hello world",
                message_id=1
            )
            
            # Проверяем что логгер был вызван
            assert mock_logger.info.called
            
            # Проверяем что print был вызван для консольного вывода
            assert mock_print.called

    def test_log_message_without_username(self):
        """Тест логирования сообщения без имени пользователя"""
        with patch('utils.logger.logger') as mock_logger, \
             patch('utils.logger.print') as mock_print:
            
            log_message(
                chat_id=12345,
                user_id=67890,
                username=None,
                message_type="TEXT",
                content="Hello world",
                message_id=1
            )
            
            assert mock_logger.info.called
            assert mock_print.called

    def test_log_message_long_content(self):
        """Тест логирования сообщения с длинным содержимым"""
        with patch('utils.logger.logger') as mock_logger, \
             patch('utils.logger.print') as mock_print:
            
            long_content = "A" * 300  # Длинное сообщение
            log_message(
                chat_id=12345,
                user_id=67890,
                username="testuser",
                message_type="TEXT",
                content=long_content,
                message_id=1
            )
            
            # Проверяем что содержимое было обрезано до 200 символов
            logged_content = mock_logger.info.call_args[0][0]
            assert len(logged_content.split("CONTENT:")[1]) <= 200

    def test_log_message_console_output(self):
        """Тест консольного вывода сообщения"""
        with patch('utils.logger.logger'), \
             patch('utils.logger.print') as mock_print:
            
            log_message(
                chat_id=12345,
                user_id=67890,
                username="testuser",
                message_type="TEXT",
                content="Hello world",
                message_id=1
            )
            
            # Проверяем что был вызов print с эмодзи
            print_calls = mock_print.call_args_list
            assert any("💬" in str(call) for call in print_calls)

    def test_log_response_success(self):
        """Тест логирования успешного ответа"""
        with patch('utils.logger.logger') as mock_logger, \
             patch('utils.logger.print') as mock_print:
            
            log_response(chat_id=12345, response_type="TEXT", success=True)
            
            assert mock_logger.info.called
            assert mock_print.called

    def test_log_response_error(self):
        """Тест логирования ответа с ошибкой"""
        with patch('utils.logger.logger') as mock_logger, \
             patch('utils.logger.print') as mock_print:
            
            log_response(
                chat_id=12345, 
                response_type="TEXT", 
                success=False, 
                error_msg="Test error"
            )
            
            assert mock_logger.info.called
            assert mock_print.called

    def test_log_response_console_output(self):
        """Тест консольного вывода ответа"""
        with patch('utils.logger.logger'), \
             patch('utils.logger.print') as mock_print:
            
            log_response(chat_id=12345, response_type="TEXT", success=True)
            
            # Проверяем что был вызов print с эмодзи
            print_calls = mock_print.call_args_list
            assert any("🤖" in str(call) for call in print_calls)

    def test_log_response_error_emoji(self):
        """Тест эмодзи для ошибки в ответе"""
        with patch('utils.logger.logger'), \
             patch('utils.logger.print') as mock_print:
            
            log_response(chat_id=12345, response_type="TEXT", success=False)
            
            # Проверяем что был вызов print с эмодзи ошибки
            print_calls = mock_print.call_args_list
            assert any("❌" in str(call) for call in print_calls)

    def test_log_update_json_basic(self):
        """Тест логирования JSON update"""
        with patch('utils.logger.logging.getLogger') as mock_get_logger:
            mock_update_logger = mock_get_logger.return_value
            
            update_data = {
                "update_id": 123,
                "message": {
                    "message_id": 1,
                    "text": "Hello",
                    "from": {
                        "id": 12345,
                        "username": "testuser",
                        "first_name": "Test"
                    }
                }
            }
            
            log_update_json(update_data)
            
            # Проверяем что был создан логгер для updates
            mock_get_logger.assert_called_with("updates")
            assert mock_update_logger.info.called

    def test_log_update_json_text_message(self):
        """Тест логирования текстового сообщения в JSON"""
        with patch('utils.logger.logging.getLogger') as mock_get_logger, \
             patch('utils.logger.logger') as mock_logger:
            
            mock_update_logger = mock_get_logger.return_value
            
            update_data = {
                "update_id": 123,
                "message": {
                    "message_id": 1,
                    "text": "Hello world",
                    "from": {
                        "id": 12345,
                        "username": "testuser",
                        "first_name": "Test"
                    }
                }
            }
            
            log_update_json(update_data)
            
            # Проверяем что был вызов основного логгера
            assert mock_logger.info.called
            
            # Проверяем что был вызов update логгера
            assert mock_update_logger.info.called

    def test_log_update_json_voice_message(self):
        """Тест логирования голосового сообщения в JSON"""
        with patch('utils.logger.logging.getLogger') as mock_get_logger, \
             patch('utils.logger.logger') as mock_logger:
            
            mock_update_logger = mock_get_logger.return_value
            
            update_data = {
                "update_id": 124,
                "message": {
                    "message_id": 2,
                    "voice": {
                        "file_id": "test_voice_id",
                        "duration": 5
                    },
                    "from": {
                        "id": 12345,
                        "username": "testuser",
                        "first_name": "Test"
                    }
                }
            }
            
            log_update_json(update_data)
            
            assert mock_logger.info.called
            assert mock_update_logger.info.called

    def test_log_update_json_callback_query(self):
        """Тест логирования callback query в JSON"""
        with patch('utils.logger.logging.getLogger') as mock_get_logger, \
             patch('utils.logger.logger') as mock_logger:
            
            mock_update_logger = mock_get_logger.return_value
            
            update_data = {
                "update_id": 125,
                "callback_query": {
                    "id": "test_callback_id",
                    "from": {
                        "id": 12345,
                        "username": "testuser",
                        "first_name": "Test"
                    },
                    "data": "test_data"
                }
            }
            
            log_update_json(update_data)
            
            assert mock_logger.info.called
            assert mock_update_logger.info.called

    def test_log_update_json_edited_message(self):
        """Тест логирования отредактированного сообщения в JSON"""
        with patch('utils.logger.logging.getLogger') as mock_get_logger, \
             patch('utils.logger.logger') as mock_logger:
            
            mock_update_logger = mock_get_logger.return_value
            
            update_data = {
                "update_id": 126,
                "edited_message": {
                    "message_id": 3,
                    "text": "Edited text",
                    "from": {
                        "id": 12345,
                        "username": "testuser",
                        "first_name": "Test"
                    }
                }
            }
            
            log_update_json(update_data)
            
            assert mock_logger.info.called
            assert mock_update_logger.info.called

    def test_log_update_json_unknown_type(self):
        """Тест логирования неизвестного типа update в JSON"""
        with patch('utils.logger.logging.getLogger') as mock_get_logger, \
             patch('utils.logger.logger') as mock_logger:
            
            mock_update_logger = mock_get_logger.return_value
            
            update_data = {
                "update_id": 127,
                "unknown_field": {
                    "data": "test"
                }
            }
            
            log_update_json(update_data)
            
            assert mock_logger.info.called
            assert mock_update_logger.info.called

    def test_log_update_json_user_info_extraction(self):
        """Тест извлечения информации о пользователе из JSON"""
        with patch('utils.logger.logging.getLogger') as mock_get_logger, \
             patch('utils.logger.logger') as mock_logger:
            
            mock_update_logger = mock_get_logger.return_value
            
            update_data = {
                "update_id": 128,
                "message": {
                    "message_id": 4,
                    "text": "Test message",
                    "from": {
                        "id": 12345,
                        "first_name": "John",
                        "last_name": "Doe"
                        # Нет username
                    }
                }
            }
            
            log_update_json(update_data)
            
            # Проверяем что информация о пользователе была извлечена
            assert mock_logger.info.called
            logged_message = mock_logger.info.call_args[0][0]
            assert "John" in logged_message

    def test_log_update_json_long_text_content(self):
        """Тест логирования длинного текстового содержимого в JSON"""
        with patch('utils.logger.logging.getLogger') as mock_get_logger, \
             patch('utils.logger.logger') as mock_logger:
            
            mock_update_logger = mock_get_logger.return_value
            
            long_text = "A" * 100  # Длинный текст
            update_data = {
                "update_id": 129,
                "message": {
                    "message_id": 5,
                    "text": long_text,
                    "from": {
                        "id": 12345,
                        "username": "testuser",
                        "first_name": "Test"
                    }
                }
            }
            
            log_update_json(update_data)
            
            assert mock_logger.info.called
            logged_message = mock_logger.info.call_args[0][0]
            # Проверяем что длинный текст был обрезан
            assert len(logged_message.split("CONTENT:")[1]) <= 50

    def test_log_message_timestamp_format(self):
        """Тест формата временной метки в логах"""
        with patch('utils.logger.logger') as mock_logger, \
             patch('utils.logger.print'):
            
            log_message(
                chat_id=12345,
                user_id=67890,
                username="testuser",
                message_type="TEXT",
                content="Hello world",
                message_id=1
            )
            
            logged_message = mock_logger.info.call_args[0][0]
            # Проверяем что временная метка в правильном формате
            assert "[" in logged_message and "]" in logged_message

    def test_log_response_timestamp_format(self):
        """Тест формата временной метки в логах ответов"""
        with patch('utils.logger.logger') as mock_logger, \
             patch('utils.logger.print'):
            
            log_response(chat_id=12345, response_type="TEXT", success=True)
            
            logged_message = mock_logger.info.call_args[0][0]
            # Проверяем что временная метка в правильном формате
            assert "[" in logged_message and "]" in logged_message

