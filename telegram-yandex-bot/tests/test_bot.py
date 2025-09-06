import unittest
from unittest.mock import patch, Mock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

class TestBot(unittest.TestCase):

    def setUp(self):
        # Mock configuration for testing
        pass

    @patch('config.config')
    def test_bot_initialization(self, mock_config):
        """Test that bot can be imported and initialized without errors"""
        # Setup mock config
        mock_config.TELEGRAM_TOKEN = "test_token"
        mock_config.YC_FOLDER_ID = "test_folder"
        mock_config.YC_API_KEY = "test_key"
        mock_config.ENABLE_VOICE = False
        mock_config.ENABLE_CONTEXT = True
        mock_config.LOG_LEVEL = "INFO"
        
        try:
            # Import bot module (this tests all imports work)
            import bot
            self.assertTrue(True)  # If import succeeded
        except Exception as e:
            self.fail(f"Bot initialization failed with exception: {e}")

    @patch('handlers.commands.get_gpt_response')
    def test_command_handlers_import(self, mock_gpt):
        """Test that command handlers can be imported"""
        mock_gpt.return_value = "Test response"
        
        try:
            from handlers.commands import start, help_command, ping_command, handle_text_message
            
            # Test that handlers exist
            self.assertTrue(callable(start))
            self.assertTrue(callable(help_command))
            self.assertTrue(callable(ping_command))
            self.assertTrue(callable(handle_text_message))
            
        except Exception as e:
            self.fail(f"Command handlers import failed with exception: {e}")

    def test_voice_handlers_import(self):
        """Test that voice handlers can be imported"""
        try:
            from handlers.voice import handle_voice_message, handle_audio_message
            
            # Test that handlers exist
            self.assertTrue(callable(handle_voice_message))
            self.assertTrue(callable(handle_audio_message))
            
        except Exception as e:
            self.fail(f"Voice handlers import failed with exception: {e}")

if __name__ == '__main__':
    unittest.main()