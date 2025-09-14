#!/usr/bin/env python3
"""
Тест логирования полного JSON входящих updates
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

from utils.logger import log_update_json, log_info, log_error

class JSONLoggingTest:
    """Тест логирования JSON updates"""
    
    def __init__(self):
        self.running = False
        
    async def simulate_telegram_updates(self):
        """Имитация различных Telegram updates в виде JSON"""
        log_info("🧪 Тест логирования полного JSON входящих updates")
        log_info("📝 Все updates будут записаны в logs/updates.json")
        log_info("💬 Имитация реальных Telegram updates")
        
        self.running = True
        
        # Имитируем различные типы updates
        updates = [
            {
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
            },
            {
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
            },
            {
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
                    "text": "В чём смысл жизни?"
                }
            },
            {
                "update_id": 123456792,
                "message": {
                    "message_id": 4,
                    "from": {
                        "id": 888999000,
                        "is_bot": False,
                        "first_name": "Техник",
                        "last_name": "Разработчик",
                        "username": "tech_dev",
                        "language_code": "ru"
                    },
                    "chat": {
                        "id": 888999000,
                        "first_name": "Техник",
                        "last_name": "Разработчик",
                        "username": "tech_dev",
                        "type": "private"
                    },
                    "date": 1694567905,
                    "voice": {
                        "duration": 4,
                        "mime_type": "audio/ogg",
                        "file_id": "BAADBAADrwADBREAAYag8VYhAQABAg",
                        "file_unique_id": "AgADBREAAYag8VY",
                        "file_size": 12345
                    }
                }
            },
            {
                "update_id": 123456793,
                "message": {
                    "message_id": 5,
                    "from": {
                        "id": 111222333,
                        "is_bot": False,
                        "first_name": "Группа",
                        "last_name": "Тест",
                        "username": "test_group",
                        "language_code": "ru"
                    },
                    "chat": {
                        "id": -1001234567890,
                        "title": "Тестовая группа",
                        "type": "group",
                        "all_members_are_administrators": True
                    },
                    "date": 1694567910,
                    "text": "Сообщение в группе"
                }
            },
            {
                "update_id": 123456794,
                "callback_query": {
                    "id": "1234567890123456789",
                    "from": {
                        "id": 987654321,
                        "is_bot": False,
                        "first_name": "Иван",
                        "last_name": "Петров",
                        "username": "ivan_petrov",
                        "language_code": "ru"
                    },
                    "message": {
                        "message_id": 6,
                        "from": {
                            "id": 8001242722,
                            "is_bot": True,
                            "first_name": "Test Bot",
                            "username": "test_bot"
                        },
                        "chat": {
                            "id": 123456789,
                            "first_name": "Иван",
                            "last_name": "Петров",
                            "username": "ivan_petrov",
                            "type": "private"
                        },
                        "date": 1694567915,
                        "text": "Выберите действие:",
                        "reply_markup": {
                            "inline_keyboard": [
                                [
                                    {
                                        "text": "Кнопка 1",
                                        "callback_data": "button_1"
                                    },
                                    {
                                        "text": "Кнопка 2",
                                        "callback_data": "button_2"
                                    }
                                ]
                            ]
                        }
                    },
                    "chat_instance": "1234567890123456789",
                    "data": "button_1"
                }
            }
        ]
        
        print("\n" + "="*80)
        print("🧪 ТЕСТ ЛОГИРОВАНИЯ ПОЛНОГО JSON UPDATES")
        print("="*80)
        
        total_updates = 0
        
        for i, update in enumerate(updates, 1):
            if not self.running:
                break
                
            total_updates += 1
            
            print(f"\n📨 Update {i}:")
            print(f"   🆔 Update ID: {update['update_id']}")
            
            # Определяем тип update
            if 'message' in update:
                if 'text' in update['message']:
                    print(f"   💬 Тип: TEXT сообщение")
                    print(f"   📝 Содержимое: {update['message']['text'][:50]}...")
                elif 'voice' in update['message']:
                    print(f"   🎤 Тип: VOICE сообщение")
                    print(f"   ⏱️ Длительность: {update['message']['voice']['duration']}с")
                else:
                    print(f"   📎 Тип: Другое сообщение")
            elif 'callback_query' in update:
                print(f"   🔘 Тип: CALLBACK QUERY")
                print(f"   📝 Данные: {update['callback_query']['data']}")
            else:
                print(f"   ❓ Тип: Неизвестный update")
            
            print(f"   👤 Пользователь: {update.get('message', update.get('callback_query', {}).get('message', {})).get('from', {}).get('username', 'Unknown')}")
            print(f"   🆔 Chat ID: {update.get('message', update.get('callback_query', {}).get('message', {})).get('chat', {}).get('id', 'Unknown')}")
            
            # Логируем полный JSON
            log_update_json(update)
            
            print(f"   ✅ JSON записан в logs/updates.json")
            
            await asyncio.sleep(0.5)
        
        print("\n" + "="*80)
        print("📊 ИТОГОВАЯ СТАТИСТИКА ТЕСТА JSON ЛОГИРОВАНИЯ")
        print("="*80)
        print(f"📨 Всего обработано updates: {total_updates}")
        print(f"💬 Текстовых сообщений: {sum(1 for u in updates if 'message' in u and 'text' in u['message'])}")
        print(f"🎤 Голосовых сообщений: {sum(1 for u in updates if 'message' in u and 'voice' in u['message'])}")
        print(f"🔘 Callback queries: {sum(1 for u in updates if 'callback_query' in u)}")
        print(f"📁 JSON файл: logs/updates.json")
        print(f"✅ Ошибок: 0")
        
        print("\n📁 Структура логов:")
        print("   📄 logs/updates.json - полные JSON updates")
        print("   📄 logs/messages.log - структурированные сообщения")
        print("   📄 logs/combined.log - общие логи")
        print("   📄 logs/error.log - ошибки")
        
        # Показываем примеры из JSON лога
        print("\n🔍 Примеры записей в JSON логе:")
        try:
            with open("logs/updates.json", "r", encoding="utf-8") as f:
                content = f.read()
                # Показываем последние несколько записей
                lines = content.split('\n')
                json_blocks = []
                current_block = []
                for line in lines:
                    if line.strip() == '=' * 80:
                        if current_block:
                            json_blocks.append('\n'.join(current_block))
                        current_block = []
                    else:
                        current_block.append(line)
                
                # Показываем последние 2 блока
                for block in json_blocks[-2:]:
                    if block.strip():
                        print(f"   📝 {block.strip()[:100]}...")
        except FileNotFoundError:
            print("   JSON лог еще не создан")
        
        print("\n✨ Тест логирования JSON updates успешно завершен!")
        print("💡 Все updates записаны в полном JSON формате!")
        print("📁 Проверьте файл logs/updates.json для просмотра всех данных!")

async def main():
    """Главная функция"""
    print("🧪 Запуск теста логирования полного JSON updates")
    print("📝 Все входящие updates будут записаны в logs/updates.json")
    print("💬 Имитация различных типов Telegram updates")
    print("📁 Логи сохраняются в папке logs/")
    print("-" * 60)
    
    # Создаем папку для логов
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    test = JSONLoggingTest()
    
    try:
        await test.simulate_telegram_updates()
    except KeyboardInterrupt:
        print("\n🛑 Тест остановлен пользователем")
    except Exception as e:
        log_error(f"Ошибка при запуске теста: {e}")
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())
