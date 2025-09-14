"""
Тесты для обработчиков голосовых сообщений.
"""
import pytest
import sys
import os
from unittest.mock import patch, Mock, AsyncMock
from io import BytesIO

# Добавляем src в путь для импортов
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from handlers.voice import handle_voice_message, handle_audio_message


@pytest.mark.handlers
class TestVoiceHandlers:
    """Тесты для обработчиков голосовых сообщений"""

    @pytest.fixture
    def mock_context(self):
        """Фикстура для создания мока контекста"""
        context = Mock()
        context.bot = Mock()
        context.bot.get_file = AsyncMock()
        context.bot.send_chat_action = AsyncMock()
        return context

    @pytest.fixture
    def mock_voice_update(self, mock_user, mock_chat, mock_voice):
        """Фикстура для создания мока Update с голосовым сообщением"""
        update = Mock()
        update.message = Mock()
        update.message.message_id = 1
        update.message.from_user = mock_user
        update.message.chat = mock_chat
        update.message.voice = mock_voice
        update.message.reply_voice = AsyncMock()
        update.effective_chat = mock_chat
        update.effective_user = mock_user
        return update

    @pytest.fixture
    def mock_file_download(self):
        """Фикстура для мока загрузки файла"""
        file_mock = Mock()
        file_mock.download_to_memory = AsyncMock()
        return file_mock

    @pytest.mark.asyncio
    async def test_handle_voice_message_voice_disabled(self, mock_voice_update, mock_context):
        """Тест обработки голосового сообщения когда голос отключен"""
        with patch('handlers.voice.config') as mock_config:
            mock_config.ENABLE_VOICE = False
            
            with patch('handlers.voice._reply_md_v2_safe', new_callable=AsyncMock) as mock_reply, \
                 patch('handlers.voice.log_response') as mock_log_response:
                
                await handle_voice_message(mock_voice_update, mock_context)
                
                # Проверяем что было отправлено сообщение об отключенных голосовых функциях
                mock_reply.assert_called_once()
                call_args = mock_reply.call_args[0][2]
                assert "Голосовые сообщения отключены" in call_args
                
                # Проверяем логирование ответа
                mock_log_response.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_voice_message_no_message(self, mock_context):
        """Тест обработки голосового сообщения без сообщения"""
        update = Mock()
        update.message = None
        update.effective_chat = None
        update.effective_user = None
        
        with patch('handlers.voice._reply_md_v2_safe', new_callable=AsyncMock) as mock_reply:
            await handle_voice_message(update, mock_context)
            
            # Ответ не должен быть отправлен
            mock_reply.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_voice_message_no_voice(self, mock_update, mock_context):
        """Тест обработки сообщения без голосового файла"""
        mock_update.message.voice = None
        
        with patch('handlers.voice._reply_md_v2_safe', new_callable=AsyncMock) as mock_reply:
            await handle_voice_message(mock_update, mock_context)
            
            # Ответ не должен быть отправлен
            mock_reply.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_voice_message_duration_limit_exceeded(self, mock_voice_update, mock_context, mock_config):
        """Тест обработки голосового сообщения превышающего лимит длительности"""
        # Устанавливаем длительность больше лимита
        mock_voice_update.message.voice.duration = 120  # Больше 60 секунд
        
        with patch('handlers.voice._reply_md_v2_safe', new_callable=AsyncMock) as mock_reply, \
             patch('handlers.voice.log_response') as mock_log_response:
            
            await handle_voice_message(mock_voice_update, mock_context)
            
            # Проверяем что было отправлено сообщение о превышении лимита
            mock_reply.assert_called_once()
            call_args = mock_reply.call_args[0][2]
            assert "слишком длинное" in call_args
            assert "60 сек" in call_args
            
            # Проверяем логирование ответа
            mock_log_response.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_voice_message_success(self, mock_voice_update, mock_context, mock_config, mock_file_download):
        """Тест успешной обработки голосового сообщения"""
        # Настраиваем моки
        mock_context.bot.get_file.return_value = mock_file_download
        mock_file_download.download_to_memory.return_value = None
        
        # Мокаем BytesIO для аудио данных
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
                
                await handle_voice_message(mock_voice_update, mock_context)
                
                # Проверяем что сообщение было залогировано
                mock_log_message.assert_called_once()
                
                # Проверяем что было отправлено сообщение о обработке
                assert mock_reply.call_count >= 2  # Сообщение о обработке + распознанный текст + ответ GPT
                
                # Проверяем что STT был вызван
                mock_stt.assert_called_once_with(audio_data)
                
                # Проверяем что GPT был вызван
                mock_gpt.assert_called_once_with("Распознанный текст", 67890)
                
                # Проверяем логирование ответов
                assert mock_log_response.call_count >= 2

    @pytest.mark.asyncio
    async def test_handle_voice_message_stt_failed(self, mock_voice_update, mock_context, mock_config, mock_file_download):
        """Тест обработки голосового сообщения когда STT не удался"""
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
                
                # Проверяем что было отправлено сообщение об ошибке распознавания
                assert mock_reply.call_count >= 2  # Сообщение о обработке + сообщение об ошибке
                
                # Проверяем содержимое сообщения об ошибке
                error_call = mock_reply.call_args_list[-1]
                error_text = error_call[0][2]
                assert "Не удалось распознать речь" in error_text
                
                # Проверяем логирование ответа
                mock_log_response.assert_called()

    @pytest.mark.asyncio
    async def test_handle_voice_message_with_tts(self, mock_voice_update, mock_context, mock_config, mock_file_download):
        """Тест обработки голосового сообщения с TTS ответом"""
        # Настраиваем моки
        mock_context.bot.get_file.return_value = mock_file_download
        mock_file_download.download_to_memory.return_value = None
        
        audio_data = b"fake_audio_data"
        tts_audio = b"fake_tts_audio"
        
        with patch('handlers.voice.io.BytesIO') as mock_bytesio:
            mock_bytesio_instance = Mock()
            mock_bytesio_instance.getvalue.return_value = audio_data
            mock_bytesio.return_value = mock_bytesio_instance
            
            with patch('handlers.voice.speech_client.speech_to_text', return_value="Распознанный текст") as mock_stt, \
                 patch('handlers.voice.get_gpt_response', return_value="Ответ от GPT") as mock_gpt, \
                 patch('handlers.voice.speech_client.text_to_speech', return_value=tts_audio) as mock_tts, \
                 patch('handlers.voice._reply_md_v2_safe', new_callable=AsyncMock) as mock_reply, \
                 patch('handlers.voice.log_message'), \
                 patch('handlers.voice.log_response') as mock_log_response, \
                 patch('handlers.voice.config') as mock_config:
                
                mock_config.ENABLE_TTS_REPLY = True
                
                await handle_voice_message(mock_voice_update, mock_context)
                
                # Проверяем что TTS был вызван
                mock_tts.assert_called_once_with("Ответ от GPT")
                
                # Проверяем что голосовое сообщение было отправлено
                mock_voice_update.message.reply_voice.assert_called_once()
                
                # Проверяем логирование голосового ответа
                assert mock_log_response.call_count >= 3  # Текст + голос

    @pytest.mark.asyncio
    async def test_handle_voice_message_tts_failed(self, mock_voice_update, mock_context, mock_config, mock_file_download):
        """Тест обработки голосового сообщения когда TTS не удался"""
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
                
                # Проверяем что голосовое сообщение НЕ было отправлено
                mock_voice_update.message.reply_voice.assert_not_called()
                
                # Проверяем логирование ошибки TTS
                assert mock_log_response.call_count >= 2

    @pytest.mark.asyncio
    async def test_handle_voice_message_download_error(self, mock_voice_update, mock_context, mock_config):
        """Тест обработки ошибки загрузки голосового файла"""
        # Настраиваем мок для ошибки загрузки
        mock_context.bot.get_file.side_effect = Exception("Download error")
        
        with patch('handlers.voice._reply_md_v2_safe', new_callable=AsyncMock) as mock_reply, \
             patch('handlers.voice.log_message'), \
             patch('handlers.voice.log_response') as mock_log_response:
            
            await handle_voice_message(mock_voice_update, mock_context)
            
            # Проверяем что было отправлено сообщение об ошибке
            mock_reply.assert_called_once()
            error_text = mock_reply.call_args[0][2]
            assert "Произошла ошибка при обработке голосового сообщения" in error_text
            
            # Проверяем логирование ошибки
            mock_log_response.assert_called()

    @pytest.mark.asyncio
    async def test_handle_voice_message_typing_status_error(self, mock_voice_update, mock_context, mock_config, mock_file_download):
        """Тест обработки ошибки отправки статуса печатания"""
        # Настраиваем моки
        mock_context.bot.get_file.return_value = mock_file_download
        mock_file_download.download_to_memory.return_value = None
        mock_context.bot.send_chat_action.side_effect = Exception("Typing error")
        
        audio_data = b"fake_audio_data"
        with patch('handlers.voice.io.BytesIO') as mock_bytesio:
            mock_bytesio_instance = Mock()
            mock_bytesio_instance.getvalue.return_value = audio_data
            mock_bytesio.return_value = mock_bytesio_instance
            
            with patch('handlers.voice.speech_client.speech_to_text', return_value="Распознанный текст") as mock_stt, \
                 patch('handlers.voice.get_gpt_response', return_value="Ответ от GPT") as mock_gpt, \
                 patch('handlers.voice._reply_md_v2_safe', new_callable=AsyncMock) as mock_reply, \
                 patch('handlers.voice.log_message'), \
                 patch('handlers.voice.log_response') as mock_log_response:
                
                await handle_voice_message(mock_voice_update, mock_context)
                
                # Проверяем что обработка продолжилась несмотря на ошибку статуса
                mock_stt.assert_called_once()
                mock_gpt.assert_called_once()
                assert mock_reply.call_count >= 2

    @pytest.mark.asyncio
    async def test_handle_audio_message_voice_disabled(self, mock_voice_update, mock_context):
        """Тест обработки аудиосообщения когда голос отключен"""
        with patch('handlers.voice.config') as mock_config:
            mock_config.ENABLE_VOICE = False
            
            with patch('handlers.voice._reply_md_v2_safe', new_callable=AsyncMock) as mock_reply:
                await handle_audio_message(mock_voice_update, mock_context)
                
                # Проверяем что было отправлено сообщение об отключенных аудиосообщениях
                mock_reply.assert_called_once()
                call_args = mock_reply.call_args[0][2]
                assert "Аудиосообщения отключены" in call_args

    @pytest.mark.asyncio
    async def test_handle_audio_message_redirects_to_voice(self, mock_voice_update, mock_context, mock_config):
        """Тест что обработчик аудиосообщений перенаправляет на обработчик голосовых"""
        with patch('handlers.voice.handle_voice_message', new_callable=AsyncMock) as mock_voice_handler:
            await handle_audio_message(mock_voice_update, mock_context)
            
            # Проверяем что был вызван обработчик голосовых сообщений
            mock_voice_handler.assert_called_once_with(mock_voice_update, mock_context)

    @pytest.mark.asyncio
    async def test_handle_voice_message_logging_content(self, mock_voice_update, mock_context, mock_config, mock_file_download):
        """Тест содержимого лога для голосового сообщения"""
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
                
                await handle_voice_message(mock_voice_update, mock_context)
                
                # Проверяем содержимое лога
                log_call = mock_log_message.call_args
                assert log_call[1]['message_type'] == "VOICE"
                assert "Voice message" in log_call[1]['content']
                assert "duration: 5s" in log_call[1]['content']
                assert "file_id: test_voice_file_id" in log_call[1]['content']

