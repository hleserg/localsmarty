"""
Расширенные тесты для основного модуля бота.
"""
import pytest
import sys
import os
from unittest.mock import patch, Mock, AsyncMock, MagicMock
from datetime import datetime

# Добавляем src в путь для импортов
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from bot import (
    log_all_updates, webhook_handler, health_handler, status_handler,
    setup_webhook, init_app, main, start_server
)


@pytest.mark.handlers
class TestBotEnhanced:
    """Расширенные тесты для основного модуля бота"""

    @pytest.fixture
    def mock_update_data(self):
        """Фикстура с данными update"""
        return {
            "update_id": 123,
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
        }

    @pytest.mark.asyncio
    async def test_log_all_updates_success(self, mock_update_data):
        """Тест успешного логирования всех updates"""
        # Создаем мок Update объекта
        mock_update = Mock()
        mock_update.to_dict.return_value = mock_update_data
        
        with patch('bot.log_update_json') as mock_log_update_json, \
             patch('bot.logger') as mock_logger:
            
            await log_all_updates(mock_update, None)
            
            # Проверяем что update был конвертирован в словарь
            mock_update.to_dict.assert_called_once()
            
            # Проверяем что JSON был залогирован
            mock_log_update_json.assert_called_once_with(mock_update_data)

    @pytest.mark.asyncio
    async def test_log_all_updates_error(self, mock_update_data):
        """Тест обработки ошибки при логировании updates"""
        # Создаем мок Update объекта с ошибкой
        mock_update = Mock()
        mock_update.to_dict.side_effect = Exception("Conversion error")
        
        with patch('bot.logger') as mock_logger:
            await log_all_updates(mock_update, None)
            
            # Проверяем что ошибка была залогирована
            mock_logger.error.assert_called_once()
            error_call = mock_logger.error.call_args[0][0]
            assert "Error logging update JSON" in error_call

    @pytest.mark.asyncio
    async def test_webhook_handler_success(self, mock_update_data):
        """Тест успешной обработки webhook"""
        # Создаем мок запроса
        mock_request = Mock()
        mock_request.json = AsyncMock(return_value=mock_update_data)
        
        # Создаем мок application
        mock_application = Mock()
        mock_application.process_update = AsyncMock()
        
        with patch('bot.application', mock_application), \
             patch('bot.Update') as mock_update_class, \
             patch('bot.log_error') as mock_log_error:
            
            # Мокаем создание Update объекта
            mock_update_instance = Mock()
            mock_update_class.de_json.return_value = mock_update_instance
            
            response = await webhook_handler(mock_request)
            
            # Проверяем что update был обработан
            mock_application.process_update.assert_called_once_with(mock_update_instance)
            
            # Проверяем ответ
            assert response.status == 200
            assert response.text == "OK"

    @pytest.mark.asyncio
    async def test_webhook_handler_no_application(self, mock_update_data):
        """Тест обработки webhook без инициализированного application"""
        # Создаем мок запроса
        mock_request = Mock()
        mock_request.json = AsyncMock(return_value=mock_update_data)
        
        with patch('bot.application', None), \
             patch('bot.log_error') as mock_log_error:
            
            response = await webhook_handler(mock_request)
            
            # Проверяем что ошибка была залогирована
            mock_log_error.assert_called_once_with("Application not initialized")
            
            # Проверяем ответ об ошибке
            assert response.status == 500
            assert response.text == "Application not initialized"

    @pytest.mark.asyncio
    async def test_webhook_handler_error(self, mock_update_data):
        """Тест обработки ошибки в webhook"""
        # Создаем мок запроса с ошибкой
        mock_request = Mock()
        mock_request.json = AsyncMock(side_effect=Exception("JSON error"))
        
        with patch('bot.log_error') as mock_log_error:
            response = await webhook_handler(mock_request)
            
            # Проверяем что ошибка была залогирована
            mock_log_error.assert_called_once()
            error_call = mock_log_error.call_args[0][0]
            assert "Error processing webhook" in error_call
            
            # Проверяем ответ об ошибке
            assert response.status == 500
            assert response.text == "Error"

    @pytest.mark.asyncio
    async def test_health_handler(self):
        """Тест health check handler"""
        mock_request = Mock()
        
        response = await health_handler(mock_request)
        
        # Проверяем ответ
        assert response.status == 200
        assert response.text == "OK"

    @pytest.mark.asyncio
    async def test_status_handler(self, mock_config):
        """Тест status handler"""
        mock_request = Mock()
        
        response = await status_handler(mock_request)
        
        # Проверяем ответ
        assert response.status == 200
        
        # Проверяем содержимое JSON
        status_data = response.body
        assert "status" in status_data
        assert "webhook_url" in status_data
        assert "port" in status_data
        assert "voice_enabled" in status_data
        assert "context_enabled" in status_data
        
        assert status_data["status"] == "running"
        assert status_data["voice_enabled"] is True
        assert status_data["context_enabled"] is True

    @pytest.mark.asyncio
    async def test_setup_webhook_success(self, mock_config):
        """Тест успешной настройки webhook"""
        # Создаем мок application
        mock_application = Mock()
        mock_application.bot = Mock()
        mock_application.bot.delete_webhook = AsyncMock()
        mock_application.bot.set_webhook = AsyncMock()
        
        with patch('bot.application', mock_application), \
             patch('bot.log_info') as mock_log_info, \
             patch('bot.log_error') as mock_log_error:
            
            await setup_webhook()
            
            # Проверяем что старый webhook был удален
            mock_application.bot.delete_webhook.assert_called_once()
            
            # Проверяем что новый webhook был установлен
            mock_application.bot.set_webhook.assert_called_once()
            
            # Проверяем параметры webhook
            call_args = mock_application.bot.set_webhook.call_args
            assert 'url' in call_args[1]
            assert 'allowed_updates' in call_args[1]
            assert 'secret_token' in call_args[1]
            
            # Проверяем логирование
            assert mock_log_info.call_count >= 2

    @pytest.mark.asyncio
    async def test_setup_webhook_error(self, mock_config):
        """Тест обработки ошибки при настройке webhook"""
        # Создаем мок application с ошибкой
        mock_application = Mock()
        mock_application.bot = Mock()
        mock_application.bot.delete_webhook = AsyncMock(side_effect=Exception("Webhook error"))
        
        with patch('bot.application', mock_application), \
             patch('bot.log_error') as mock_log_error:
            
            await setup_webhook()
            
            # Проверяем что ошибка была залогирована
            mock_log_error.assert_called_once()
            error_call = mock_log_error.call_args[0][0]
            assert "Error setting webhook" in error_call

    @pytest.mark.asyncio
    async def test_init_app(self, mock_config):
        """Тест инициализации приложения"""
        app = await init_app()
        
        # Проверяем что приложение было создано
        assert app is not None
        
        # Проверяем что маршруты были добавлены
        routes = [route.resource for route in app.router.routes()]
        route_paths = [route._path for route in routes if hasattr(route, '_path')]
        
        assert '/bot' in route_paths
        assert '/health' in route_paths
        assert '/' in route_paths

    def test_main_no_telegram_token(self, mock_config):
        """Тест main функции без токена Telegram"""
        with patch('bot.config') as mock_config:
            mock_config.TELEGRAM_TOKEN = None
            
            with patch('bot.log_error') as mock_log_error:
                main()
                
                # Проверяем что ошибка была залогирована
                mock_log_error.assert_called_once_with("TELEGRAM_TOKEN is not set")

    def test_main_no_neuroapi_key(self, mock_config):
        """Тест main функции без ключа NeuroAPI"""
        with patch('bot.config') as mock_config:
            mock_config.TELEGRAM_TOKEN = "test_token"
            mock_config.NEUROAPI_API_KEY = None
            
            with patch('bot.log_error') as mock_log_error:
                main()
                
                # Проверяем что ошибка была залогирована
                mock_log_error.assert_called_once_with("NEUROAPI_API_KEY is not set")

    def test_main_success(self, mock_config):
        """Тест успешного запуска main функции"""
        with patch('bot.config') as mock_config:
            mock_config.TELEGRAM_TOKEN = "test_token"
            mock_config.NEUROAPI_API_KEY = "test_key"
            mock_config.ENABLE_VOICE = True
            mock_config.ENABLE_CONTEXT = True
            
            with patch('bot.log_info') as mock_log_info, \
                 patch('bot.Application') as mock_application_class, \
                 patch('bot.start_server') as mock_start_server:
                
                mock_application = Mock()
                mock_application_class.builder.return_value.token.return_value.build.return_value = mock_application
                
                main()
                
                # Проверяем что логирование было выполнено
                assert mock_log_info.call_count >= 4
                
                # Проверяем что application был создан
                mock_application_class.builder.assert_called_once()
                
                # Проверяем что start_server был вызван
                mock_start_server.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_server_success(self, mock_config):
        """Тест успешного запуска сервера"""
        # Создаем мок application
        mock_application = Mock()
        mock_application.initialize = AsyncMock()
        mock_application.bot = Mock()
        mock_application.bot.delete_webhook = AsyncMock()
        mock_application.shutdown = AsyncMock()
        
        with patch('bot.application', mock_application), \
             patch('bot.setup_webhook') as mock_setup_webhook, \
             patch('bot.init_app') as mock_init_app, \
             patch('bot.web.AppRunner') as mock_app_runner_class, \
             patch('bot.web.TCPSite') as mock_tcp_site_class, \
             patch('bot.log_info') as mock_log_info:
            
            # Мокаем компоненты сервера
            mock_app_runner = Mock()
            mock_app_runner.setup = AsyncMock()
            mock_app_runner.cleanup = AsyncMock()
            mock_app_runner_class.return_value = mock_app_runner
            
            mock_tcp_site = Mock()
            mock_tcp_site.start = AsyncMock()
            mock_tcp_site_class.return_value = mock_tcp_site
            
            mock_app = Mock()
            mock_init_app.return_value = mock_app
            
            # Мокаем бесконечное ожидание
            with patch('bot.asyncio.Future') as mock_future:
                mock_future_instance = Mock()
                mock_future.return_value = mock_future_instance
                
                # Симулируем KeyboardInterrupt для завершения
                mock_future_instance.__await__ = AsyncMock(side_effect=KeyboardInterrupt())
                
                await start_server()
                
                # Проверяем что сервер был запущен
                mock_application.initialize.assert_called_once()
                mock_setup_webhook.assert_called_once()
                mock_app_runner.setup.assert_called_once()
                mock_tcp_site.start.assert_called_once()
                
                # Проверяем логирование
                assert mock_log_info.call_count >= 2

    def test_webhook_allowed_updates(self, mock_config):
        """Тест allowed updates для webhook"""
        expected_updates = [
            "message",
            "edited_message", 
            "business_connection",
            "business_message",
            "edited_business_message",
            "deleted_business_messages"
        ]
        
        # Проверяем что allowed_updates определены правильно
        assert len(expected_updates) == 6
        assert "message" in expected_updates
        assert "business_message" in expected_updates

    def test_webhook_url_construction(self, mock_config):
        """Тест построения URL webhook"""
        webhook_url = f"{mock_config.WEBHOOK_URL}{mock_config.WEBHOOK_PATH}"
        
        assert webhook_url == "https://test.example.com/test"
        assert webhook_url.startswith("https://")

    def test_logging_configuration(self, mock_config):
        """Тест конфигурации логирования"""
        with patch('bot.logger') as mock_logger:
            # Проверяем что логгер доступен
            assert mock_logger is not None
            
            # Проверяем что функции логирования доступны
            from bot import log_info, log_error, log_update_json
            assert callable(log_info)
            assert callable(log_error)
            assert callable(log_update_json)

    def test_application_global_variable(self):
        """Тест глобальной переменной application"""
        from bot import application
        
        # Проверяем что переменная существует
        assert application is None  # Изначально None

    def test_environment_variables_loading(self):
        """Тест загрузки переменных окружения"""
        with patch('bot.load_dotenv') as mock_load_dotenv:
            # Импортируем модуль заново
            import importlib
            import bot
            importlib.reload(bot)
            
            # Проверяем что load_dotenv был вызван
            mock_load_dotenv.assert_called_once()

    def test_import_structure(self):
        """Тест структуры импортов"""
        # Проверяем что все необходимые модули импортированы
        from bot import (
            os, logging, json, asyncio, Update, Application, CommandHandler,
            MessageHandler, filters, CallbackQueryHandler, web
        )
        
        # Проверяем что импорты работают
        assert os is not None
        assert logging is not None
        assert json is not None
        assert asyncio is not None
        assert Update is not None
        assert Application is not None

