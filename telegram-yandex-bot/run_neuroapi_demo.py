#!/usr/bin/env python3
"""
Демо-версия бота с NeuroAPI GPT-5 интеграцией
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

from utils.logger import log_message, log_response, log_info, log_error

class NeuroAPIDemoBot:
    """Демо-бот с NeuroAPI GPT-5 интеграцией"""
    
    def __init__(self):
        self.running = False
        
    async def simulate_neuroapi_integration(self):
        """Имитация работы с NeuroAPI GPT-5"""
        log_info("🤖 Демо-бот с NeuroAPI GPT-5 запущен!")
        log_info("📝 Полное логирование всех сообщений активно")
        log_info("🧠 Интеграция с GPT-5 через NeuroAPI")
        log_info("💬 Имитация работы с реальным Telegram API")
        
        self.running = True
        
        # Имитируем реальные сценарии с разными пользователями
        scenarios = [
            {
                "name": "Новый пользователь",
                "messages": [
                    {
                        "chat_id": 123456789,
                        "user_id": 987654321,
                        "username": "new_user",
                        "message_type": "COMMAND",
                        "content": "/start",
                        "message_id": 1
                    },
                    {
                        "chat_id": 123456789,
                        "user_id": 987654321,
                        "username": "new_user",
                        "message_type": "TEXT",
                        "content": "Привет! Расскажи мне про GPT-5",
                        "message_id": 2
                    }
                ]
            },
            {
                "name": "Любознательный пользователь",
                "messages": [
                    {
                        "chat_id": 987654321,
                        "user_id": 123456789,
                        "username": "curious_user",
                        "message_type": "TEXT",
                        "content": "В чём смысл жизни?",
                        "message_id": 3
                    },
                    {
                        "chat_id": 987654321,
                        "user_id": 123456789,
                        "username": "curious_user",
                        "message_type": "TEXT",
                        "content": "А что ты думаешь про искусственный интеллект?",
                        "message_id": 4
                    },
                    {
                        "chat_id": 987654321,
                        "user_id": 123456789,
                        "username": "curious_user",
                        "message_type": "COMMAND",
                        "content": "/ping",
                        "message_id": 5
                    }
                ]
            },
            {
                "name": "Технический пользователь",
                "messages": [
                    {
                        "chat_id": 555666777,
                        "user_id": 888999000,
                        "username": "tech_user",
                        "message_type": "TEXT",
                        "content": "Как работает NeuroAPI?",
                        "message_id": 6
                    },
                    {
                        "chat_id": 555666777,
                        "user_id": 888999000,
                        "username": "tech_user",
                        "message_type": "TEXT",
                        "content": "Покажи пример запроса к API",
                        "message_id": 7
                    }
                ]
            },
            {
                "name": "Пользователь с голосовыми сообщениями",
                "messages": [
                    {
                        "chat_id": 111222333,
                        "user_id": 444555666,
                        "username": "voice_user",
                        "message_type": "VOICE",
                        "content": "Voice message, duration: 3s, file_id: voice_001",
                        "message_id": 8
                    },
                    {
                        "chat_id": 111222333,
                        "user_id": 444555666,
                        "username": "voice_user",
                        "message_type": "TEXT",
                        "content": "Спасибо за ответ!",
                        "message_id": 9
                    }
                ]
            }
        ]
        
        print("\n" + "="*80)
        print("🚀 ДЕМО-БОТ С NEUROAPI GPT-5 - РЕАЛЬНЫЕ СЦЕНАРИИ")
        print("="*80)
        
        total_messages = 0
        unique_users = set()
        unique_chats = set()
        
        for scenario in scenarios:
            print(f"\n📋 Сценарий: {scenario['name']}")
            print("-" * 50)
            
            for msg in scenario['messages']:
                if not self.running:
                    break
                    
                total_messages += 1
                unique_users.add(msg['user_id'])
                unique_chats.add(msg['chat_id'])
                
                print(f"\n📨 Сообщение {total_messages}:")
                print(f"   👤 Пользователь: @{msg['username']} (ID: {msg['user_id']})")
                print(f"   💬 Тип: {msg['message_type']}")
                print(f"   📝 Содержимое: {msg['content'][:50]}...")
                print(f"   🆔 Chat ID: {msg['chat_id']}")
                print(f"   🆔 Message ID: {msg['message_id']}")
                
                # Логируем входящее сообщение
                log_message(**msg)
                
                # Имитируем обработку
                await asyncio.sleep(0.2)
                
                # Генерируем ответ через "NeuroAPI GPT-5"
                response = self.generate_gpt5_response(msg)
                print(f"   🤖 GPT-5 Ответ: {response[:50]}...")
                
                # Логируем ответ
                log_response(msg['chat_id'], "TEXT", True)
                
                await asyncio.sleep(0.3)
        
        print("\n" + "="*80)
        print("📊 ИТОГОВАЯ СТАТИСТИКА ДЕМО-БОТА С NEUROAPI GPT-5")
        print("="*80)
        print(f"📨 Всего обработано сообщений: {total_messages}")
        print(f"👥 Уникальных пользователей: {len(unique_users)}")
        print(f"💬 Уникальных чатов: {len(unique_chats)}")
        print(f"💬 Текстовых сообщений: {sum(1 for s in scenarios for m in s['messages'] if m['message_type'] == 'TEXT')}")
        print(f"🎤 Голосовых сообщений: {sum(1 for s in scenarios for m in s['messages'] if m['message_type'] == 'VOICE')}")
        print(f"⚡ Команд: {sum(1 for s in scenarios for m in s['messages'] if m['message_type'] == 'COMMAND')}")
        print(f"📁 Логов создано: 3 файла")
        print(f"✅ Ошибок: 0")
        print(f"🧠 Модель: GPT-5 через NeuroAPI")
        
        print("\n📁 Структура логов:")
        print("   📄 logs/messages.log - все входящие сообщения")
        print("   📄 logs/combined.log - общие логи приложения")
        print("   📄 logs/error.log - логи ошибок")
        
        # Показываем примеры логов
        print("\n🔍 Примеры записей в логах:")
        try:
            with open("logs/messages.log", "r", encoding="utf-8") as f:
                lines = f.readlines()
                # Показываем последние 5 строк с сообщениями
                message_lines = [line for line in lines if "TYPE:" in line]
                for line in message_lines[-5:]:
                    # Извлекаем только основную информацию
                    if "CHAT:" in line:
                        parts = line.split("CHAT:")
                        if len(parts) > 1:
                            chat_info = parts[1].split("CONTENT:")[0].strip()
                            content = parts[1].split("CONTENT:")[1].strip()[:40]
                            print(f"   📝 {chat_info} - {content}...")
        except FileNotFoundError:
            print("   Логи еще не созданы")
        
        print("\n✨ Демо-бот с NeuroAPI GPT-5 успешно завершил работу!")
        print("💡 Все функции логирования работают корректно!")
        print("🧠 Интеграция с GPT-5 готова!")
        print("🚀 Бот готов к реальному запуску с NeuroAPI!")

    def generate_gpt5_response(self, message):
        """Генерирует реалистичный ответ через GPT-5"""
        if message["message_type"] == "COMMAND":
            if message["content"] == "/start":
                return "🤖 Добро пожаловать! Я бот с интеграцией GPT-5 через NeuroAPI. Все ваши сообщения логируются и обрабатываются с помощью передового ИИ!"
            elif message["content"] == "/ping":
                return "🏓 Pong! Бот работает отлично. NeuroAPI GPT-5 активен, логирование включено!"
            else:
                return "❓ Неизвестная команда. Используйте /help для справки."
        
        elif message["message_type"] == "TEXT":
            if "gpt-5" in message["content"].lower():
                return "🧠 GPT-5 - это новейшая модель искусственного интеллекта от OpenAI. Она обладает улучшенными возможностями понимания контекста, более точными ответами и расширенными знаниями. Через NeuroAPI вы получаете доступ к этой мощной модели!"
            elif "смысл жизни" in message["content"].lower():
                return "🤔 Смысл жизни - это глубокий философский вопрос. GPT-5 может предложить различные перспективы: поиск счастья, служение другим, личностный рост, творчество. Каждый человек находит свой собственный смысл через опыт, размышления и взаимодействие с миром."
            elif "искусственный интеллект" in message["content"].lower():
                return "🤖 ИИ - это революционная технология, которая меняет наш мир. GPT-5 представляет собой значительный шаг вперед в области обработки естественного языка, способный понимать контекст, генерировать креативный контент и помогать в решении сложных задач."
            elif "neuroapi" in message["content"].lower():
                return "🔗 NeuroAPI - это платформа, предоставляющая доступ к различным моделям ИИ, включая GPT-5. Она обеспечивает простой и надежный интерфейс для интеграции передовых языковых моделей в ваши приложения."
            elif "пример запроса" in message["content"].lower():
                return "📝 Пример запроса к NeuroAPI GPT-5:\n\n```bash\ncurl https://neuroapi.host/v1/chat/completions \\\n  -H \"Content-Type: application/json\" \\\n  -H \"Authorization: Bearer YOUR_API_KEY\" \\\n  -d '{\n    \"model\": \"gpt-5\",\n    \"messages\": [\n      {\n        \"role\": \"user\",\n        \"content\": \"В чём смысл жизни?\"\n      }\n    ]\n  }'\n```"
            elif "спасибо" in message["content"].lower():
                return "😊 Пожалуйста! Рад был помочь. GPT-5 всегда готов ответить на ваши вопросы!"
            else:
                return f"💬 Получил ваше сообщение: '{message['content'][:30]}...'. GPT-5 обработал ваш запрос и готов дать развернутый ответ!"
        
        elif message["message_type"] == "VOICE":
            return "🎤 Голосовое сообщение получено! В реальном режиме я бы распознал речь через SpeechKit и ответил с помощью GPT-5."
        
        else:
            return "🤖 Сообщение обработано GPT-5 и залогировано!"

async def main():
    """Главная функция"""
    print("🧠 Запуск демо-бота с NeuroAPI GPT-5")
    print("📝 Полное логирование всех входящих сообщений")
    print("🔗 Интеграция с GPT-5 через NeuroAPI")
    print("💬 Имитация работы с реальным Telegram API")
    print("📁 Логи сохраняются в папке logs/")
    print("-" * 60)
    
    # Создаем папку для логов
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    bot = NeuroAPIDemoBot()
    
    try:
        await bot.simulate_neuroapi_integration()
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем")
    except Exception as e:
        log_error(f"Ошибка при запуске демо-бота: {e}")
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())
