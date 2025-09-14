"""
Тесты производительности для Telegram бота.
"""
import pytest
import sys
import os
import time
import asyncio
from unittest.mock import patch, Mock, AsyncMock

# Добавляем src в путь для импортов
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))


@pytest.mark.slow
class TestPerformance:
    """Тесты производительности"""

    @pytest.fixture
    def mock_context(self):
        """Фикстура для создания мока контекста"""
        context = Mock()
        context.bot = Mock()
        context.bot.send_message = AsyncMock()
        context.bot.send_chat_action = AsyncMock()
        return context

    def test_neuroapi_response_time(self, mock_config):
        """Тест времени ответа NeuroAPI"""
        from services.neuroapi_client import NeuroAPIClient
        
        with patch('services.neuroapi_client.requests.post') as mock_post:
            # Мокаем быстрый ответ
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{
                    "message": {
                        "content": "Быстрый ответ"
                    }
                }]
            }
            mock_post.return_value = mock_response
            
            client = NeuroAPIClient()
            
            # Измеряем время ответа
            start_time = time.time()
            response = client.get_response("Тест", 12345)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # Проверяем что ответ получен быстро (менее 1 секунды для мока)
            assert response_time < 1.0
            assert response == "Быстрый ответ"

    def test_speech_client_response_time(self, mock_config):
        """Тест времени ответа Speech клиента"""
        from services.speech_client import SpeechClient
        
        with patch('services.speech_client.requests.post') as mock_post:
            # Мокаем быстрый ответ
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"result": "Распознанный текст"}
            mock_post.return_value = mock_response
            
            client = SpeechClient()
            
            # Измеряем время STT
            start_time = time.time()
            result = client.speech_to_text(b"fake_audio_data")
            end_time = time.time()
            
            stt_time = end_time - start_time
            
            # Проверяем что STT выполняется быстро
            assert stt_time < 1.0
            assert result == "Распознанный текст"

    def test_context_management_performance(self, mock_config):
        """Тест производительности управления контекстом"""
        from services.neuroapi_client import NeuroAPIClient
        
        client = NeuroAPIClient()
        
        # Измеряем время обновления контекста
        start_time = time.time()
        
        # Добавляем много сообщений
        for i in range(100):
            client._update_context(12345, f"Сообщение {i}", f"Ответ {i}")
        
        end_time = time.time()
        context_time = end_time - start_time
        
        # Проверяем что обновление контекста быстрое
        assert context_time < 0.1  # Менее 100мс для 100 сообщений
        
        # Проверяем что контекст был обрезан
        context = client.chat_contexts[12345]
        assert len(context) == 20  # Должно быть обрезано до 20

    def test_markdown_processing_performance(self):
        """Тест производительности обработки Markdown"""
        from utils.markdown import transform_to_markdown_v2
        
        # Создаем длинный текст с форматированием
        long_text = "**Жирный текст** и __курсив__ " * 1000
        
        # Измеряем время обработки
        start_time = time.time()
        result = transform_to_markdown_v2(long_text)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Проверяем что обработка быстрая
        assert processing_time < 0.1  # Менее 100мс для длинного текста
        assert len(result) > 0

    def test_logging_performance(self):
        """Тест производительности логирования"""
        from utils.logger import log_message, log_response
        
        # Измеряем время логирования
        start_time = time.time()
        
        # Логируем много сообщений
        for i in range(100):
            log_message(
                chat_id=12345,
                user_id=67890,
                username="testuser",
                message_type="TEXT",
                content=f"Сообщение {i}",
                message_id=i
            )
            log_response(12345, "TEXT", True)
        
        end_time = time.time()
        logging_time = end_time - start_time
        
        # Проверяем что логирование быстрое
        assert logging_time < 0.5  # Менее 500мс для 200 логов

    @pytest.mark.asyncio
    async def test_handler_performance(self, mock_update, mock_context, mock_config):
        """Тест производительности обработчиков"""
        from handlers.commands import handle_text_message
        
        with patch('handlers.commands.get_gpt_response', return_value="Быстрый ответ") as mock_gpt, \
             patch('handlers.commands._send_typing_status', new_callable=AsyncMock), \
             patch('handlers.commands._reply_md_v2_safe', new_callable=AsyncMock), \
             patch('handlers.commands.log_message'), \
             patch('handlers.commands.log_response'):
            
            # Измеряем время обработки
            start_time = time.time()
            await handle_text_message(mock_update, mock_context)
            end_time = time.time()
            
            handler_time = end_time - start_time
            
            # Проверяем что обработчик быстрый
            assert handler_time < 0.1  # Менее 100мс для мока

    def test_config_loading_performance(self):
        """Тест производительности загрузки конфигурации"""
        from config import Config
        
        # Измеряем время создания конфигурации
        start_time = time.time()
        config = Config()
        end_time = time.time()
        
        config_time = end_time - start_time
        
        # Проверяем что конфигурация загружается быстро
        assert config_time < 0.01  # Менее 10мс

    def test_memory_usage_context_management(self, mock_config):
        """Тест использования памяти при управлении контекстом"""
        import psutil
        import os
        
        from services.neuroapi_client import NeuroAPIClient
        
        # Получаем начальное использование памяти
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        client = NeuroAPIClient()
        
        # Добавляем много контекстов
        for chat_id in range(1000):
            client._update_context(chat_id, f"Сообщение {chat_id}", f"Ответ {chat_id}")
        
        # Получаем использование памяти после добавления контекстов
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Проверяем что увеличение памяти разумное (менее 10MB)
        assert memory_increase < 10 * 1024 * 1024  # 10MB
        
        # Проверяем что контексты были обрезаны
        total_contexts = sum(len(context) for context in client.chat_contexts.values())
        assert total_contexts <= 1000 * 20  # Максимум 20 сообщений на чат

    def test_concurrent_requests_performance(self, mock_config):
        """Тест производительности при одновременных запросах"""
        from services.neuroapi_client import NeuroAPIClient
        import threading
        import queue
        
        with patch('services.neuroapi_client.requests.post') as mock_post:
            # Мокаем ответы
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
            
            client = NeuroAPIClient()
            results = queue.Queue()
            
            def make_request(chat_id):
                """Выполняет запрос"""
                start_time = time.time()
                response = client.get_response("Тест", chat_id)
                end_time = time.time()
                results.put((chat_id, response, end_time - start_time))
            
            # Создаем несколько потоков
            threads = []
            for i in range(10):
                thread = threading.Thread(target=make_request, args=(i,))
                threads.append(thread)
                thread.start()
            
            # Ждем завершения всех потоков
            for thread in threads:
                thread.join()
            
            # Проверяем результаты
            assert results.qsize() == 10
            
            # Проверяем что все запросы выполнились быстро
            while not results.empty():
                chat_id, response, response_time = results.get()
                assert response == "Ответ"
                assert response_time < 1.0

    def test_large_message_processing_performance(self, mock_config):
        """Тест производительности обработки больших сообщений"""
        from services.neuroapi_client import NeuroAPIClient
        
        with patch('services.neuroapi_client.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{
                    "message": {
                        "content": "Ответ на большое сообщение"
                    }
                }]
            }
            mock_post.return_value = mock_response
            
            client = NeuroAPIClient()
            
            # Создаем большое сообщение
            large_message = "A" * 10000  # 10KB сообщение
            
            # Измеряем время обработки
            start_time = time.time()
            response = client.get_response(large_message, 12345)
            end_time = time.time()
            
            processing_time = end_time - start_time
            
            # Проверяем что обработка быстрая даже для больших сообщений
            assert processing_time < 1.0
            assert response == "Ответ на большое сообщение"

    def test_json_processing_performance(self):
        """Тест производительности обработки JSON"""
        import json
        
        # Создаем большой JSON объект
        large_data = {
            "updates": [
                {
                    "update_id": i,
                    "message": {
                        "message_id": i,
                        "text": f"Сообщение {i}",
                        "from": {"id": i, "username": f"user{i}"},
                        "chat": {"id": i, "type": "private"}
                    }
                }
                for i in range(1000)
            ]
        }
        
        # Измеряем время сериализации
        start_time = time.time()
        json_str = json.dumps(large_data, ensure_ascii=False)
        end_time = time.time()
        
        serialize_time = end_time - start_time
        
        # Измеряем время десериализации
        start_time = time.time()
        parsed_data = json.loads(json_str)
        end_time = time.time()
        
        deserialize_time = end_time - start_time
        
        # Проверяем что JSON обработка быстрая
        assert serialize_time < 0.1
        assert deserialize_time < 0.1
        assert len(parsed_data["updates"]) == 1000

    def test_string_operations_performance(self):
        """Тест производительности строковых операций"""
        from utils.markdown import escape_markdown_v2, transform_to_markdown_v2
        
        # Создаем строку с множеством специальных символов
        special_text = "**Жирный** __курсив__ `код` [ссылка](url) (скобки) _подчеркивание_ *звездочки* " * 100
        
        # Измеряем время экранирования
        start_time = time.time()
        escaped = escape_markdown_v2(special_text)
        end_time = time.time()
        
        escape_time = end_time - start_time
        
        # Измеряем время преобразования
        start_time = time.time()
        transformed = transform_to_markdown_v2(special_text)
        end_time = time.time()
        
        transform_time = end_time - start_time
        
        # Проверяем что строковые операции быстрые
        assert escape_time < 0.1
        assert transform_time < 0.1
        assert len(escaped) > 0
        assert len(transformed) > 0

