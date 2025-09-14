#!/usr/bin/env python3
"""
Демо-версия webhook сервера для тестирования
"""

import os
import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime

# Добавляем src в путь Python
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from utils.logger import log_info, log_error

class WebhookDemo:
    """Демо webhook сервера"""
    
    def __init__(self):
        self.running = False
        
    async def simulate_webhook_requests(self):
        """Имитация webhook запросов от Telegram"""
        log_info("🌐 Демо webhook сервера запущено!")
        log_info("📡 Имитация входящих webhook запросов")
        log_info("💬 Симуляция различных типов updates")
        
        self.running = True
        
        # Имитируем различные webhook запросы
        webhook_requests = [
            {
                "name": "Текстовое сообщение",
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
                "name": "Обычное сообщение",
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
                "name": "Голосовое сообщение",
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
                "name": "Callback Query",
                "data": {
                    "update_id": 123456792,
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
                            "message_id": 4,
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
            }
        ]
        
        print("\n" + "="*80)
        print("🌐 ДЕМО WEBHOOK СЕРВЕРА - СИМУЛЯЦИЯ ЗАПРОСОВ")
        print("="*80)
        
        total_requests = 0
        
        for i, request in enumerate(webhook_requests, 1):
            if not self.running:
                break
                
            total_requests += 1
            
            print(f"\n📡 Webhook запрос {i}: {request['name']}")
            print("-" * 50)
            
            # Имитируем получение webhook запроса
            data_size = len(json.dumps(request['data']))
            print(f"📥 Получен webhook запрос: {data_size} байт")
            print(f"🆔 Update ID: {request['data']['update_id']}")
            
            # Определяем тип update
            if 'message' in request['data']:
                if 'text' in request['data']['message']:
                    print(f"💬 Тип: TEXT сообщение")
                    print(f"📝 Содержимое: {request['data']['message']['text'][:50]}...")
                elif 'voice' in request['data']['message']:
                    print(f"🎤 Тип: VOICE сообщение")
                    print(f"⏱️ Длительность: {request['data']['message']['voice']['duration']}с")
                else:
                    print(f"📎 Тип: Другое сообщение")
            elif 'callback_query' in request['data']:
                print(f"🔘 Тип: CALLBACK QUERY")
                print(f"📝 Данные: {request['data']['callback_query']['data']}")
            else:
                print(f"❓ Тип: Неизвестный update")
            
            # Получаем информацию о пользователе
            user_info = "Unknown"
            if 'message' in request['data']:
                from_user = request['data']['message'].get('from', {})
                username = from_user.get('username')
                first_name = from_user.get('first_name', "")
                if username:
                    user_info = f"@{username}"
                elif first_name:
                    user_info = first_name
            elif 'callback_query' in request['data']:
                from_user = request['data']['callback_query'].get('from', {})
                username = from_user.get('username')
                first_name = from_user.get('first_name', "")
                if username:
                    user_info = f"@{username}"
                elif first_name:
                    user_info = first_name
            
            print(f"👤 Пользователь: {user_info}")
            
            # Имитируем обработку
            print(f"🔄 Обрабатываем update...")
            await asyncio.sleep(0.3)
            
            # Имитируем ответ
            print(f"✅ Update обработан успешно")
            print(f"📤 Отправляем ответ: OK (200)")
            
            await asyncio.sleep(0.5)
        
        print("\n" + "="*80)
        print("📊 ИТОГОВАЯ СТАТИСТИКА ДЕМО WEBHOOK СЕРВЕРА")
        print("="*80)
        print(f"📡 Всего webhook запросов: {total_requests}")
        print(f"💬 Текстовых сообщений: {sum(1 for r in webhook_requests if 'message' in r['data'] and 'text' in r['data']['message'])}")
        print(f"🎤 Голосовых сообщений: {sum(1 for r in webhook_requests if 'message' in r['data'] and 'voice' in r['data']['message'])}")
        print(f"🔘 Callback queries: {sum(1 for r in webhook_requests if 'callback_query' in r['data'])}")
        print(f"✅ Успешно обработано: {total_requests}")
        print(f"❌ Ошибок: 0")
        
        print("\n📁 Структура webhook сервера:")
        print("   🌐 Webhook endpoint: /webhook")
        print("   ❤️ Health check: /health")
        print("   🔒 SSL поддержка: включена")
        print("   📝 Логирование: полное")
        
        print("\n🚀 Преимущества webhook режима:")
        print("   ⚡ Быстрая обработка updates")
        print("   🔄 Автоматическое восстановление")
        print("   📊 Масштабируемость")
        print("   🛡️ Безопасность")
        print("   📈 Мониторинг")
        
        print("\n✨ Демо webhook сервера успешно завершено!")
        print("💡 Webhook сервер готов к развертыванию!")
        print("🐳 Docker Compose конфигурация готова!")
        print("🔐 SSL сертификаты можно сгенерировать!")

async def main():
    """Главная функция"""
    print("🌐 Запуск демо webhook сервера")
    print("📡 Имитация входящих webhook запросов")
    print("💬 Симуляция различных типов updates")
    print("📁 Подготовка к развертыванию")
    print("-" * 60)
    
    # Создаем папку для логов
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    demo = WebhookDemo()
    
    try:
        await demo.simulate_webhook_requests()
    except KeyboardInterrupt:
        print("\n🛑 Демо остановлено пользователем")
    except Exception as e:
        log_error(f"Ошибка при запуске демо: {e}")
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())
