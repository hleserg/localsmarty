#!/usr/bin/env python3
"""
Тест улучшенного консольного логирования
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from datetime import datetime

# Добавляем src в путь Python
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from utils.logger import log_update_json, log_message, log_response, log_info, log_error

class ConsoleLoggingTest:
    """Тест улучшенного консольного логирования"""
    
    def __init__(self):
        self.running = False
        
    async def simulate_console_logging(self):
        """Имитация различных событий с консольным выводом"""
        print("🖥️ ТЕСТ УЛУЧШЕННОГО КОНСОЛЬНОГО ЛОГИРОВАНИЯ")
        print("="*60)
        
        log_info("🚀 Запуск теста консольного логирования")
        log_info("📝 Все события будут выведены в консоль с эмодзи")
        log_info("💬 Имитация реальных событий бота")
        
        self.running = True
        
        # Имитируем различные события
        events = [
            {
                "type": "startup",
                "message": "Бот запущен и готов к работе"
            },
            {
                "type": "update",
                "data": {
                    "update_id": 123456789,
                    "message": {
                        "message_id": 1,
                        "from": {
                            "id": 987654321,
                            "is_bot": False,
                            "first_name": "Иван",
                            "last_name": "Петров",
                            "username": "ivan_petrov",
                            "language_code": "ru"
                        },
                        "chat": {
                            "id": 123456789,
                            "first_name": "Иван",
                            "last_name": "Петров",
                            "username": "ivan_petrov",
                            "type": "private"
                        },
                        "date": 1694567890,
                        "text": "/start"
                    }
                }
            },
            {
                "type": "message",
                "data": {
                    "chat_id": 123456789,
                    "user_id": 987654321,
                    "username": "ivan_petrov",
                    "message_type": "COMMAND",
                    "content": "/start",
                    "message_id": 1
                }
            },
            {
                "type": "response",
                "data": {
                    "chat_id": 123456789,
                    "response_type": "TEXT",
                    "success": True
                }
            },
            {
                "type": "update",
                "data": {
                    "update_id": 123456790,
                    "message": {
                        "message_id": 2,
                        "from": {
                            "id": 987654321,
                            "is_bot": False,
                            "first_name": "Иван",
                            "last_name": "Петров",
                            "username": "ivan_petrov",
                            "language_code": "ru"
                        },
                        "chat": {
                            "id": 123456789,
                            "first_name": "Иван",
                            "last_name": "Петров",
                            "username": "ivan_petrov",
                            "type": "private"
                        },
                        "date": 1694567895,
                        "text": "Привет! Расскажи мне про GPT-5"
                    }
                }
            },
            {
                "type": "message",
                "data": {
                    "chat_id": 123456789,
                    "user_id": 987654321,
                    "username": "ivan_petrov",
                    "message_type": "TEXT",
                    "content": "Привет! Расскажи мне про GPT-5",
                    "message_id": 2
                }
            },
            {
                "type": "response",
                "data": {
                    "chat_id": 123456789,
                    "response_type": "TEXT",
                    "success": True
                }
            },
            {
                "type": "update",
                "data": {
                    "update_id": 123456791,
                    "message": {
                        "message_id": 3,
                        "from": {
                            "id": 555666777,
                            "is_bot": False,
                            "first_name": "Анна",
                            "last_name": "Сидорова",
                            "username": "anna_sidorova",
                            "language_code": "ru"
                        },
                        "chat": {
                            "id": 555666777,
                            "first_name": "Анна",
                            "last_name": "Сидорова",
                            "username": "anna_sidorova",
                            "type": "private"
                        },
                        "date": 1694567900,
                        "voice": {
                            "duration": 4,
                            "mime_type": "audio/ogg",
                            "file_id": "BAADBAADrwADBREAAYag8VYhAQABAg",
                            "file_unique_id": "AgADBREAAYag8VY",
                            "file_size": 12345
                        }
                    }
                }
            },
            {
                "type": "message",
                "data": {
                    "chat_id": 555666777,
                    "user_id": 555666777,
                    "username": "anna_sidorova",
                    "message_type": "VOICE",
                    "content": "Voice message, duration: 4s, file_id: voice_001",
                    "message_id": 3
                }
            },
            {
                "type": "response",
                "data": {
                    "chat_id": 555666777,
                    "response_type": "TEXT",
                    "success": True
                }
            },
            {
                "type": "error",
                "message": "Тестовая ошибка для демонстрации"
            }
        ]
        
        print("\n📋 Сценарии событий:")
        print("-" * 40)
        
        for i, event in enumerate(events, 1):
            if not self.running:
                break
                
            print(f"\n🎬 Событие {i}: {event['type'].upper()}")
            
            if event["type"] == "startup":
                log_info(event["message"])
                
            elif event["type"] == "update":
                log_update_json(event["data"])
                
            elif event["type"] == "message":
                log_message(**event["data"])
                
            elif event["type"] == "response":
                log_response(**event["data"])
                
            elif event["type"] == "error":
                log_error(event["message"])
            
            await asyncio.sleep(0.5)
        
        print("\n" + "="*60)
        print("📊 ИТОГОВАЯ СТАТИСТИКА ТЕСТА КОНСОЛЬНОГО ЛОГИРОВАНИЯ")
        print("="*60)
        print(f"📨 Всего событий: {len(events)}")
        print(f"🔄 Updates: {sum(1 for e in events if e['type'] == 'update')}")
        print(f"💬 Сообщения: {sum(1 for e in events if e['type'] == 'message')}")
        print(f"🤖 Ответы: {sum(1 for e in events if e['type'] == 'response')}")
        print(f"❌ Ошибки: {sum(1 for e in events if e['type'] == 'error')}")
        print(f"✅ Успешных операций: {sum(1 for e in events if e['type'] == 'response' and e['data']['success'])}")
        
        print("\n📁 Структура логов:")
        print("   📄 logs/updates.json - полные JSON updates")
        print("   📄 logs/messages.log - структурированные сообщения")
        print("   📄 logs/combined.log - общие логи")
        print("   📄 logs/error.log - ошибки")
        print("   🖥️ Консоль - краткая информация с эмодзи")
        
        print("\n✨ Тест консольного логирования успешно завершен!")
        print("💡 Все события выведены в консоль с эмодзи!")
        print("📝 Подробные логи сохранены в файлы!")
        print("🖥️ Консольный вывод улучшен для удобства!")

async def main():
    """Главная функция"""
    print("🖥️ Запуск теста улучшенного консольного логирования")
    print("📝 Все события будут выведены в консоль с эмодзи")
    print("💬 Имитация различных событий бота")
    print("📁 Подробные логи сохраняются в файлы")
    print("-" * 60)
    
    # Создаем папку для логов
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    test = ConsoleLoggingTest()
    
    try:
        await test.simulate_console_logging()
    except KeyboardInterrupt:
        print("\n🛑 Тест остановлен пользователем")
    except Exception as e:
        log_error(f"Ошибка при запуске теста: {e}")
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())
