"""
Тесты для обработчиков команд.
"""
import pytest
import sys
import os
from unittest.mock import patch, Mock, AsyncMock

# Добавляем src в путь для импортов
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from handlers.commands import start, help_command, ping_command, handle_text_message, handle_business_message


@pytest.mark.handlers
class TestCommandHandlers:
    """Тесты для обработчиков команд"""

    @pytest.fixture
    def mock_context(self):
        """Фикстура для создания мока контекста"""
        context = Mock()
        context.bot = Mock()
        context.bot.send_message = AsyncMock()
        context.bot.send_chat_action = AsyncMock()
        return context

    @pytest.mark.asyncio
    async def test_start_command_success(self, mock_update, mock_context, mock_config):
        """Тест успешного выполнения команды /start"""
        with patch('handlers.commands._reply_md_v2_safe', new_callable=AsyncMock) as mock_reply, \
             patch('handlers.commands.log_message') as mock_log_message, \
             patch('handlers.commands.log_response') as mock_log_response:
            
            await start(mock_update, mock_context)
            
            # Проверяем что сообщение было залогировано
            mock_log_message.assert_called_once()
            
            # Проверяем что ответ был отправлен
            mock_reply.assert_called_once()
            
            # Проверяем что ответ был залогирован
            mock_log_response.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_command_missing_message(self, mock_context):
        """Тест команды /start с отсутствующим сообщением"""
        update = Mock()
        update.message = None
        update.effective_chat = None
        update.effective_user = None
        
        with patch('handlers.commands._reply_md_v2_safe', new_callable=AsyncMock) as mock_reply:
            await start(update, mock_context)
            
            # Ответ не должен быть отправлен
            mock_reply.assert_not_called()

    @pytest.mark.asyncio
    async def test_start_command_welcome_message_content(self, mock_update, mock_context, mock_config):
        """Тест содержимого приветственного сообщения"""
        with patch('handlers.commands._reply_md_v2_safe', new_callable=AsyncMock) as mock_reply:
            await start(mock_update, mock_context)
            
            # Проверяем содержимое сообщения
            call_args = mock_reply.call_args
            message_text = call_args[0][2]  # Третий аргумент - текст
            
            assert "Привет! Я бот с интеграцией GPT-5" in message_text
            assert "Контекст диалога: включен" in message_text
            assert "Голосовые сообщения: поддерживаются" in message_text

    @pytest.mark.asyncio
    async def test_help_command_success(self, mock_update, mock_context, mock_config):
        """Тест успешного выполнения команды /help"""
        with patch('handlers.commands._reply_md_v2_safe', new_callable=AsyncMock) as mock_reply, \
             patch('handlers.commands.log_message') as mock_log_message, \
             patch('handlers.commands.log_response') as mock_log_response:
            
            await help_command(mock_update, mock_context)
            
            mock_log_message.assert_called_once()
            mock_reply.assert_called_once()
            mock_log_response.assert_called_once()

    @pytest.mark.asyncio
    async def test_help_command_content(self, mock_update, mock_context, mock_config):
        """Тест содержимого справочного сообщения"""
        with patch('handlers.commands._reply_md_v2_safe', new_callable=AsyncMock) as mock_reply:
            await help_command(mock_update, mock_context)
            
            call_args = mock_reply.call_args
            message_text = call_args[0][2]
            
            assert "Доступные команды:" in message_text
            assert "/start" in message_text
            assert "/help" in message_text
            assert "/ping" in message_text
            assert "Голосовые сообщения:" in message_text
            assert "Контекст:" in message_text

    @pytest.mark.asyncio
    async def test_help_command_voice_disabled(self, mock_update, mock_context):
        """Тест справочного сообщения когда голос отключен"""
        with patch('handlers.commands._reply_md_v2_safe', new_callable=AsyncMock) as mock_reply, \
             patch('handlers.commands.config') as mock_config:
            mock_config.ENABLE_VOICE = False
            mock_config.ENABLE_CONTEXT = True
            
            await help_command(mock_update, mock_context)
            
            call_args = mock_reply.call_args
            message_text = call_args[0][2]
            
            assert "Голосовые сообщения:" not in message_text
            assert "Контекст:" in message_text

    @pytest.mark.asyncio
    async def test_ping_command_success(self, mock_update, mock_context, mock_config):
        """Тест успешного выполнения команды /ping"""
        with patch('handlers.commands._reply_md_v2_safe', new_callable=AsyncMock) as mock_reply, \
             patch('handlers.commands.log_message') as mock_log_message, \
             patch('handlers.commands.log_response') as mock_log_response:
            
            await ping_command(mock_update, mock_context)
            
            mock_log_message.assert_called_once()
            mock_reply.assert_called_once()
            mock_log_response.assert_called_once()

    @pytest.mark.asyncio
    async def test_ping_command_content(self, mock_update, mock_context, mock_config):
        """Тест содержимого ping сообщения"""
        with patch('handlers.commands._reply_md_v2_safe', new_callable=AsyncMock) as mock_reply:
            await ping_command(mock_update, mock_context)
            
            call_args = mock_reply.call_args
            message_text = call_args[0][2]
            
            assert "Pong!" in message_text
            assert "Бот работает нормально" in message_text
            assert "Версия: 1.0.0" in message_text
            assert "NeuroAPI GPT-5: ✅ настроен" in message_text
            assert "Голосовые функции: ✅ включены" in message_text

    @pytest.mark.asyncio
    async def test_ping_command_no_api_key(self, mock_update, mock_context):
        """Тест ping команды без API ключа"""
        with patch('handlers.commands._reply_md_v2_safe', new_callable=AsyncMock) as mock_reply, \
             patch('handlers.commands.config') as mock_config:
            mock_config.NEUROAPI_API_KEY = None
            mock_config.ENABLE_VOICE = True
            
            await ping_command(mock_update, mock_context)
            
            call_args = mock_reply.call_args
            message_text = call_args[0][2]
            
            assert "NeuroAPI GPT-5: ❌ не настроен" in message_text

    @pytest.mark.asyncio
    async def test_handle_text_message_success(self, mock_update, mock_context, mock_config):
        """Тест успешной обработки текстового сообщения"""
        with patch('handlers.commands.get_gpt_response', return_value="Тестовый ответ") as mock_gpt, \
             patch('handlers.commands._send_typing_status', new_callable=AsyncMock) as mock_typing, \
             patch('handlers.commands._reply_md_v2_safe', new_callable=AsyncMock) as mock_reply, \
             patch('handlers.commands.log_message') as mock_log_message, \
             patch('handlers.commands.log_response') as mock_log_response:
            
            await handle_text_message(mock_update, mock_context)
            
            # Проверяем что статус "печатает" был отправлен
            mock_typing.assert_called_once()
            
            # Проверяем что GPT был вызван
            mock_gpt.assert_called_once_with("Тестовое сообщение", 67890)
            
            # Проверяем что ответ был отправлен
            mock_reply.assert_called_once()
            
            # Проверяем логирование
            mock_log_message.assert_called_once()
            mock_log_response.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_text_message_business_message(self, mock_business_update, mock_context):
        """Тест обработки текстового сообщения как бизнес-сообщения"""
        with patch('handlers.commands.handle_business_message', new_callable=AsyncMock) as mock_business_handler:
            await handle_text_message(mock_business_update, mock_context)
            
            # Проверяем что был вызван обработчик бизнес-сообщений
            mock_business_handler.assert_called_once_with(mock_business_update, mock_context)

    @pytest.mark.asyncio
    async def test_handle_text_message_error(self, mock_update, mock_context):
        """Тест обработки ошибки при обработке текстового сообщения"""
        with patch('handlers.commands.get_gpt_response', side_effect=Exception("GPT Error")) as mock_gpt, \
             patch('handlers.commands._send_typing_status', new_callable=AsyncMock), \
             patch('handlers.commands.log_message'), \
             patch('handlers.commands.log_response') as mock_log_response:
            
            # Мокаем отправку сообщения об ошибке
            mock_context.bot.send_message = AsyncMock()
            
            await handle_text_message(mock_update, mock_context)
            
            # Проверяем что ошибка была залогирована
            mock_log_response.assert_called()
            
            # Проверяем что было отправлено сообщение об ошибке
            mock_context.bot.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_business_message_success(self, mock_business_update, mock_context, mock_config):
        """Тест успешной обработки бизнес-сообщения"""
        with patch('handlers.commands.get_gpt_response', return_value="Бизнес ответ") as mock_gpt, \
             patch('handlers.commands._send_business_typing_status', new_callable=AsyncMock) as mock_typing, \
             patch('handlers.commands._reply_business_md_v2_safe', new_callable=AsyncMock) as mock_reply, \
             patch('handlers.commands.log_message') as mock_log_message, \
             patch('handlers.commands.log_response') as mock_log_response:
            
            await handle_business_message(mock_business_update, mock_context)
            
            # Проверяем что статус "печатает" был отправлен
            mock_typing.assert_called_once()
            
            # Проверяем что GPT был вызван с правильными параметрами
            mock_gpt.assert_called_once_with(
                "Тестовое бизнес-сообщение", 
                67890, 
                is_business_message=True, 
                business_connection_id="test_business_connection_id"
            )
            
            # Проверяем что ответ был отправлен
            mock_reply.assert_called_once()
            
            # Проверяем логирование
            mock_log_message.assert_called_once()
            mock_log_response.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_business_message_no_business_message(self, mock_context):
        """Тест обработки бизнес-сообщения без business_message"""
        update = Mock()
        update.business_message = None
        update.effective_chat = None
        update.effective_user = None
        
        with patch('handlers.commands._reply_business_md_v2_safe', new_callable=AsyncMock) as mock_reply:
            await handle_business_message(update, mock_context)
            
            # Ответ не должен быть отправлен
            mock_reply.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_business_message_error(self, mock_business_update, mock_context):
        """Тест обработки ошибки при обработке бизнес-сообщения"""
        with patch('handlers.commands.get_gpt_response', side_effect=Exception("Business Error")) as mock_gpt, \
             patch('handlers.commands._send_business_typing_status', new_callable=AsyncMock), \
             patch('handlers.commands.log_message'), \
             patch('handlers.commands.log_response') as mock_log_response, \
             patch('handlers.commands._reply_business_md_v2_safe', new_callable=AsyncMock) as mock_reply:
            
            await handle_business_message(mock_business_update, mock_context)
            
            # Проверяем что ошибка была залогирована
            mock_log_response.assert_called()
            
            # Проверяем что было отправлено сообщение об ошибке
            mock_reply.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_typing_status_success(self, mock_update, mock_context):
        """Тест успешной отправки статуса печатания"""
        from handlers.commands import _send_typing_status
        
        await _send_typing_status(mock_update, mock_context)
        
        # Проверяем что статус был отправлен
        mock_context.bot.send_chat_action.assert_called_once_with(
            chat_id=67890, 
            action="typing"
        )

    @pytest.mark.asyncio
    async def test_send_typing_status_no_message(self, mock_context):
        """Тест отправки статуса печатания без сообщения"""
        from handlers.commands import _send_typing_status
        
        update = Mock()
        update.message = None
        update.effective_chat = None
        
        await _send_typing_status(update, mock_context)
        
        # Статус не должен быть отправлен
        mock_context.bot.send_chat_action.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_business_typing_status_success(self, mock_business_update, mock_context):
        """Тест успешной отправки статуса печатания для бизнес-сообщения"""
        from handlers.commands import _send_business_typing_status
        
        await _send_business_typing_status(mock_business_update, mock_context)
        
        # Проверяем что статус был отправлен
        mock_context.bot.send_chat_action.assert_called_once_with(
            chat_id=67890, 
            action="typing"
        )

    @pytest.mark.asyncio
    async def test_send_business_typing_status_no_business_message(self, mock_context):
        """Тест отправки статуса печатания без бизнес-сообщения"""
        from handlers.commands import _send_business_typing_status
        
        update = Mock()
        update.business_message = None
        update.effective_chat = None
        
        await _send_business_typing_status(update, mock_context)
        
        # Статус не должен быть отправлен
        mock_context.bot.send_chat_action.assert_not_called()

    @pytest.mark.asyncio
    async def test_reply_md_v2_safe_success(self, mock_update, mock_context):
        """Тест успешной отправки ответа с MarkdownV2"""
        from handlers.commands import _reply_md_v2_safe
        
        with patch('handlers.commands.transform_to_markdown_v2', return_value="*Formatted text*") as mock_transform:
            await _reply_md_v2_safe(mock_update, mock_context, "Test text")
            
            # Проверяем что текст был отформатирован
            mock_transform.assert_called_once_with("Test text")
            
            # Проверяем что сообщение было отправлено
            mock_context.bot.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_reply_md_v2_safe_bad_request_fallback(self, mock_update, mock_context):
        """Тест fallback на обычный текст при BadRequest"""
        from handlers.commands import _reply_md_v2_safe
        from telegram.error import BadRequest
        
        # Первый вызов вызывает BadRequest, второй успешен
        mock_context.bot.send_message.side_effect = [
            BadRequest("Markdown error"),
            Mock()  # Успешный вызов
        ]
        
        with patch('handlers.commands.transform_to_markdown_v2', return_value="*Formatted text*") as mock_transform:
            await _reply_md_v2_safe(mock_update, mock_context, "Test text")
            
            # Проверяем что было два вызова send_message
            assert mock_context.bot.send_message.call_count == 2

    @pytest.mark.asyncio
    async def test_reply_business_md_v2_safe_success(self, mock_business_update, mock_context):
        """Тест успешной отправки бизнес-ответа с MarkdownV2"""
        from handlers.commands import _reply_business_md_v2_safe
        
        with patch('handlers.commands.transform_to_markdown_v2', return_value="*Formatted text*") as mock_transform:
            await _reply_business_md_v2_safe(mock_business_update, mock_context, "Test text")
            
            # Проверяем что текст был отформатирован
            mock_transform.assert_called_once_with("Test text")
            
            # Проверяем что сообщение было отправлено с business_connection_id
            mock_context.bot.send_message.assert_called_once()
            call_kwargs = mock_context.bot.send_message.call_args[1]
            assert call_kwargs['business_connection_id'] == "test_business_connection_id"

