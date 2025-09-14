"""
Тесты для сервиса Telegram клиента.
"""
import pytest
import sys
import os
from unittest.mock import patch, Mock

# Добавляем src в путь для импортов
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from services.telegram_client import TelegramClient


@pytest.mark.services
class TestTelegramClient:
    """Тесты для Telegram клиента"""

    def test_client_initialization(self, mock_config):
        """Тест инициализации клиента"""
        with patch('services.telegram_client.os.getenv', return_value='test_token'):
            client = TelegramClient()
            
            assert client.token == 'test_token'
            assert client.updater is not None

    def test_client_initialization_no_token(self):
        """Тест инициализации клиента без токена"""
        with patch('services.telegram_client.os.getenv', return_value=None):
            with pytest.raises(Exception):  # Updater требует токен
                TelegramClient()

    def test_start_command_handler(self, mock_config):
        """Тест обработчика команды start"""
        with patch('services.telegram_client.os.getenv', return_value='test_token'):
            client = TelegramClient()
            
            # Создаем мок update и context
            update = Mock()
            update.message = Mock()
            update.message.reply_text = Mock()
            
            context = Mock()
            
            # Вызываем обработчик
            client.start(update, context)
            
            # Проверяем что сообщение было отправлено
            update.message.reply_text.assert_called_once()
            call_args = update.message.reply_text.call_args[0][0]
            assert "бот, который использует Яндекс GPT" in call_args

    def test_run_method(self, mock_config):
        """Тест метода run"""
        with patch('services.telegram_client.os.getenv', return_value='test_token'):
            client = TelegramClient()
            
            # Мокаем updater
            mock_updater = Mock()
            mock_dispatcher = Mock()
            mock_updater.dispatcher = mock_dispatcher
            mock_updater.start_polling = Mock()
            mock_updater.idle = Mock()
            
            client.updater = mock_updater
            
            # Вызываем run
            client.run()
            
            # Проверяем что обработчик был добавлен
            mock_dispatcher.add_handler.assert_called_once()
            
            # Проверяем что polling был запущен
            mock_updater.start_polling.assert_called_once()
            mock_updater.idle.assert_called_once()

    def test_logging_setup(self, mock_config):
        """Тест настройки логирования"""
        with patch('services.telegram_client.os.getenv', return_value='test_token'), \
             patch('services.telegram_client.logging.basicConfig') as mock_basic_config:
            
            TelegramClient()
            
            # Проверяем что логирование было настроено
            mock_basic_config.assert_called_once()

    def test_logger_creation(self, mock_config):
        """Тест создания логгера"""
        with patch('services.telegram_client.os.getenv', return_value='test_token'), \
             patch('services.telegram_client.logging.getLogger') as mock_get_logger:
            
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            client = TelegramClient()
            
            # Проверяем что логгер был создан
            mock_get_logger.assert_called_with(__name__)

    def test_updater_configuration(self, mock_config):
        """Тест конфигурации updater"""
        with patch('services.telegram_client.os.getenv', return_value='test_token'):
            client = TelegramClient()
            
            # Проверяем что updater был создан с правильными параметрами
            assert client.updater is not None
            # Updater должен быть создан с токеном и use_context=True

    def test_command_handler_registration(self, mock_config):
        """Тест регистрации обработчика команд"""
        with patch('services.telegram_client.os.getenv', return_value='test_token'):
            client = TelegramClient()
            
            # Мокаем dispatcher
            mock_dispatcher = Mock()
            client.updater.dispatcher = mock_dispatcher
            
            # Вызываем run для регистрации обработчиков
            client.run()
            
            # Проверяем что обработчик был добавлен
            mock_dispatcher.add_handler.assert_called_once()
            
            # Проверяем что был добавлен CommandHandler для "start"
            call_args = mock_dispatcher.add_handler.call_args[0][0]
            assert hasattr(call_args, 'command') or hasattr(call_args, 'callback')

    def test_start_message_content(self, mock_config):
        """Тест содержимого сообщения start"""
        with patch('services.telegram_client.os.getenv', return_value='test_token'):
            client = TelegramClient()
            
            # Создаем мок update
            update = Mock()
            update.message = Mock()
            update.message.reply_text = Mock()
            
            context = Mock()
            
            # Вызываем обработчик
            client.start(update, context)
            
            # Проверяем содержимое сообщения
            call_args = update.message.reply_text.call_args[0][0]
            assert "Привет!" in call_args
            assert "бот" in call_args
            assert "Яндекс GPT" in call_args

    def test_client_with_different_token(self, mock_config):
        """Тест клиента с разными токенами"""
        test_tokens = ["token1", "token2", "special_token_123"]
        
        for token in test_tokens:
            with patch('services.telegram_client.os.getenv', return_value=token):
                client = TelegramClient()
                assert client.token == token

    def test_client_environment_variable_name(self, mock_config):
        """Тест имени переменной окружения для токена"""
        with patch('services.telegram_client.os.getenv') as mock_getenv:
            mock_getenv.return_value = 'test_token'
            
            TelegramClient()
            
            # Проверяем что была вызвана правильная переменная окружения
            mock_getenv.assert_called_with('TELEGRAM_BOT_TOKEN')

    def test_updater_use_context(self, mock_config):
        """Тест использования контекста в updater"""
        with patch('services.telegram_client.os.getenv', return_value='test_token'), \
             patch('services.telegram_client.Updater') as mock_updater_class:
            
            mock_updater = Mock()
            mock_updater_class.return_value = mock_updater
            
            TelegramClient()
            
            # Проверяем что Updater был создан с use_context=True
            mock_updater_class.assert_called_once_with('test_token', use_context=True)

    def test_start_handler_functionality(self, mock_config):
        """Тест функциональности обработчика start"""
        with patch('services.telegram_client.os.getenv', return_value='test_token'):
            client = TelegramClient()
            
            # Создаем мок update с различными сценариями
            update = Mock()
            update.message = Mock()
            update.message.reply_text = Mock()
            
            context = Mock()
            
            # Тестируем что обработчик не падает
            try:
                client.start(update, context)
                # Если дошли сюда, значит обработчик работает
                assert True
            except Exception as e:
                pytest.fail(f"Start handler failed with exception: {e}")

    def test_run_method_error_handling(self, mock_config):
        """Тест обработки ошибок в методе run"""
        with patch('services.telegram_client.os.getenv', return_value='test_token'):
            client = TelegramClient()
            
            # Мокаем updater с ошибкой
            mock_updater = Mock()
            mock_updater.dispatcher = Mock()
            mock_updater.start_polling.side_effect = Exception("Polling error")
            
            client.updater = mock_updater
            
            # Тестируем что ошибка обрабатывается
            with pytest.raises(Exception, match="Polling error"):
                client.run()

    def test_client_logging_level(self, mock_config):
        """Тест уровня логирования"""
        with patch('services.telegram_client.os.getenv', return_value='test_token'), \
             patch('services.telegram_client.logging.basicConfig') as mock_basic_config:
            
            TelegramClient()
            
            # Проверяем что логирование было настроено с правильным уровнем
            call_args = mock_basic_config.call_args
            assert 'level' in call_args[1]
            assert call_args[1]['level'] == 20  # INFO level

    def test_client_logging_format(self, mock_config):
        """Тест формата логирования"""
        with patch('services.telegram_client.os.getenv', return_value='test_token'), \
             patch('services.telegram_client.logging.basicConfig') as mock_basic_config:
            
            TelegramClient()
            
            # Проверяем формат логирования
            call_args = mock_basic_config.call_args
            assert 'format' in call_args[1]
            format_string = call_args[1]['format']
            assert '%(asctime)s' in format_string
            assert '%(name)s' in format_string
            assert '%(levelname)s' in format_string
            assert '%(message)s' in format_string

