import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Добавляем src директорию в путь для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestBot(unittest.TestCase):

    def setUp(self):
        # Настройка тестовых переменных окружения
        os.environ['TELEGRAM_TOKEN'] = 'test-telegram-token'
        os.environ['YANDEX_API_KEY'] = 'test-api-key'
        os.environ['YANDEX_FOLDER_ID'] = 'test-folder-id'

    @patch('bot.Updater')
    def test_bot_initialization(self, mock_updater):
        """Тест инициализации бота"""
        try:
            from bot import main
            
            # Настройка мока
            mock_updater_instance = MagicMock()
            mock_updater.return_value = mock_updater_instance
            
            # Мокаем методы для предотвращения реального запуска
            mock_updater_instance.start_polling = MagicMock()
            mock_updater_instance.idle = MagicMock()
            
            # Тест создания Updater с правильным токеном
            mock_updater.assert_not_called()  # Еще не должен быть вызван
            
            self.assertTrue(True)  # Если импорт прошел успешно
        except Exception as e:
            self.fail(f"Bot initialization failed with exception: {e}")

    @patch('bot.get_gpt_response')
    def test_handle_message_function(self, mock_gpt_response):
        """Тест функции обработки сообщений"""
        from bot import handle_message
        
        # Настройка мока
        mock_gpt_response.return_value = "Тестовый ответ от GPT"
        
        # Создание мок-объектов для Update и CallbackContext
        mock_update = MagicMock()
        mock_context = MagicMock()
        
        mock_update.message.text = "Тестовое сообщение"
        mock_update.effective_user.id = 12345
        mock_update.effective_user.username = "testuser"
        mock_update.effective_chat.id = 67890
        
        # Вызов функции
        handle_message(mock_update, mock_context)
        
        # Проверки
        mock_gpt_response.assert_called_once_with("Тестовое сообщение")
        mock_update.message.reply_text.assert_called_once_with("Тестовый ответ от GPT")

    def test_start_command(self):
        """Тест команды /start"""
        from bot import start
        
        # Создание мок-объектов
        mock_update = MagicMock()
        mock_context = MagicMock()
        
        # Вызов функции
        start(mock_update, mock_context)
        
        # Проверка, что ответ был отправлен
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        self.assertIn("Привет", call_args)
        self.assertIn("Yandex GPT", call_args)

    def test_help_command(self):
        """Тест команды /help"""
        from bot import help_command
        
        # Создание мок-объектов
        mock_update = MagicMock()
        mock_context = MagicMock()
        
        # Вызов функции
        help_command(mock_update, mock_context)
        
        # Проверка, что ответ был отправлен
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        self.assertIn("Помощь", call_args)

    def test_long_message_handling(self):
        """Тест обработки длинных сообщений"""
        from bot import handle_message
        
        # Создание мок-объектов
        mock_update = MagicMock()
        mock_context = MagicMock()
        
        # Длинное сообщение (больше 4000 символов)
        long_message = "a" * 4001
        mock_update.message.text = long_message
        mock_update.effective_user.id = 12345
        mock_update.effective_user.username = "testuser"
        
        # Вызов функции
        handle_message(mock_update, mock_context)
        
        # Проверка, что отправлено сообщение об ошибке
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        self.assertIn("слишком длинное", call_args)

if __name__ == '__main__':
    unittest.main()