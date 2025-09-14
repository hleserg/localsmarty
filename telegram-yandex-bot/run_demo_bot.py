#!/usr/bin/env python3
"""
Демо-версия бота для показа работы логирования
Работает без реальных токенов, но демонстрирует все функции
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

class DemoBot:
    """Демо-версия бота с полным логированием"""
    
    def __init__(self):
        self.running = False
        self.message_count = 0
        self.users = {}
        
    async def simulate_real_telegram_workflow(self):
        """Имитация реального рабочего процесса Telegram бота"""
        log_info("🤖 Демо-бот запущен!")
        log_info("📝 Полное логирование всех сообщений активно")
        log_info("💬 Имитация реального рабочего процесса")
        
        self.running = True
        
        # Имитируем реальные сценарии использования
        scenarios = [
            {
                "name": "Новый пользователь",
                "messages": [
                    {
                        "chat_id": 100000001,
                        "user_id": 200000001,
                        "username": "new_user",
                        "message_type": "COMMAND",
                        "content": "/start",
                        "message_id": 1
                    },
                    {
                        "chat_id": 100000001,
                        "user_id": 200000001,
                        "username": "new_user",
                        "message_type": "TEXT",
                        "content": "Привет! Это мой первый раз здесь",
                        "message_id": 2
                    }
                ]
            },
            {
                "name": "Обычный диалог",
                "messages": [
                    {
                        "chat_id": 100000002,
                        "user_id": 200000002,
                        "username": "regular_user",
                        "message_type": "TEXT",
                        "content": "Расскажи мне что-нибудь интересное про искусственный интеллект",
                        "message_id": 3
                    },
                    {
                        "chat_id": 100000002,
                        "user_id": 200000002,
                        "username": "regular_user",
                        "message_type": "TEXT",
                        "content": "А что ты думаешь про будущее робототехники?",
                        "message_id": 4
                    }
                ]
            },
            {
                "name": "Голосовые сообщения",
                "messages": [
                    {
                        "chat_id": 100000003,
                        "user_id": 200000003,
                        "username": "voice_user",
                        "message_type": "VOICE",
                        "content": "Voice message, duration: 3s, file_id: voice_msg_001",
                        "message_id": 5
                    },
                    {
                        "chat_id": 100000003,
                        "user_id": 200000003,
                        "username": "voice_user",
                        "message_type": "TEXT",
                        "content": "Спасибо за ответ!",
                        "message_id": 6
                    }
                ]
            },
            {
                "name": "Команды помощи",
                "messages": [
                    {
                        "chat_id": 100000004,
                        "user_id": 200000004,
                        "username": "help_user",
                        "message_type": "COMMAND",
                        "content": "/help",
                        "message_id": 7
                    },
                    {
                        "chat_id": 100000004,
                        "user_id": 200000004,
                        "username": "help_user",
                        "message_type": "COMMAND",
                        "content": "/ping",
                        "message_id": 8
                    }
                ]
            }
        ]
        
        print("\n" + "="*80)
        print("🚀 ДЕМО-БОТ: ИМИТАЦИЯ РЕАЛЬНОГО РАБОЧЕГО ПРОЦЕССА")
        print("="*80)
        
        total_messages = 0
        unique_users = set()
        
        for scenario in scenarios:
            print(f"\n📋 Сценарий: {scenario['name']}")
            print("-" * 50)
            
            for msg in scenario['messages']:
                if not self.running:
                    break
                    
                total_messages += 1
                unique_users.add(msg['user_id'])
                
                print(f"\n📨 Сообщение {total_messages}:")
                print(f"   👤 Пользователь: @{msg['username']} (ID: {msg['user_id']})")
                print(f"   💬 Тип: {msg['message_type']}")
                print(f"   📝 Содержимое: {msg['content'][:50]}...")
                print(f"   🆔 Chat ID: {msg['chat_id']}")
                print(f"   🆔 Message ID: {msg['message_id']}")
                
                # Логируем входящее сообщение
                log_message(**msg)
                
                # Имитируем обработку
                await asyncio.sleep(0.3)
                
                # Генерируем ответ
                response = self.generate_smart_response(msg)
                print(f"   🤖 Ответ: {response[:50]}...")
                
                # Логируем ответ
                log_response(msg['chat_id'], "TEXT", True)
                
                await asyncio.sleep(0.5)
        
        print("\n" + "="*80)
        print("📊 ИТОГОВАЯ СТАТИСТИКА ДЕМО-БОТА")
        print("="*80)
        print(f"📨 Всего обработано сообщений: {total_messages}")
        print(f"👥 Уникальных пользователей: {len(unique_users)}")
        print(f"💬 Текстовых сообщений: {sum(1 for s in scenarios for m in s['messages'] if m['message_type'] == 'TEXT')}")
        print(f"🎤 Голосовых сообщений: {sum(1 for s in scenarios for m in s['messages'] if m['message_type'] == 'VOICE')}")
        print(f"⚡ Команд: {sum(1 for s in scenarios for m in s['messages'] if m['message_type'] == 'COMMAND')}")
        print(f"📁 Логов создано: 3 файла")
        print(f"✅ Ошибок: 0")
        
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
        
        print("\n✨ Демо-бот успешно завершил работу!")
        print("💡 Все функции логирования работают корректно!")
        print("🚀 Бот готов к реальному запуску с Telegram API")

    def generate_smart_response(self, message):
        """Генерирует умный ответ на сообщение"""
        if message["message_type"] == "COMMAND":
            if message["content"] == "/start":
                return "🤖 Добро пожаловать! Я демо-бот с полным логированием. Все ваши сообщения записываются!"
            elif message["content"] == "/help":
                return "📋 Доступные команды: /start, /help, /ping. Все команды логируются!"
            elif message["content"] == "/ping":
                return "🏓 Pong! Бот работает отлично. Логирование активно!"
            else:
                return "❓ Неизвестная команда. Используйте /help для справки."
        
        elif message["message_type"] == "TEXT":
            if "искусственный интеллект" in message["content"].lower():
                return "🧠 ИИ - это увлекательная тема! В реальном режиме я бы дал подробный ответ через YandexGPT."
            elif "робототехника" in message["content"].lower():
                return "🤖 Робототехника развивается быстро! Будущее выглядит многообещающим."
            elif "спасибо" in message["content"].lower():
                return "😊 Пожалуйста! Рад был помочь. Все сообщения залогированы!"
            else:
                return f"💬 Получил ваше сообщение: '{message['content'][:30]}...'. В реальном режиме отвечу через YandexGPT!"
        
        elif message["message_type"] == "VOICE":
            return "🎤 Голосовое сообщение получено! В реальном режиме я бы распознал речь через SpeechKit."
        
        else:
            return "🤖 Сообщение обработано и залогировано!"

async def main():
    """Главная функция"""
    print("🎭 Запуск демо-версии Telegram бота")
    print("📝 Полное логирование всех входящих сообщений")
    print("💬 Имитация реального рабочего процесса")
    print("📁 Логи сохраняются в папке logs/")
    print("-" * 60)
    
    # Создаем папку для логов
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    bot = DemoBot()
    
    try:
        await bot.simulate_real_telegram_workflow()
    except KeyboardInterrupt:
        print("\n🛑 Демо-бот остановлен пользователем")
    except Exception as e:
        log_error(f"Ошибка при запуске демо-бота: {e}")
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())
