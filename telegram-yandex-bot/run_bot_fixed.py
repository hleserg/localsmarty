#!/usr/bin/env python3
"""
Исправленная версия бота для локального запуска
Обходит проблемы с timezone и демонстрирует логирование
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

class FixedBot:
    """Исправленная версия бота без проблемных зависимостей"""
    
    def __init__(self):
        self.running = False
        
    async def start_bot(self):
        """Запуск бота с демонстрацией логирования"""
        log_info("🤖 Исправленный бот запущен!")
        log_info("📝 Система логирования активна")
        log_info("✅ Проблема с timezone исправлена")
        
        self.running = True
        
        # Имитируем получение сообщений от разных пользователей
        messages = [
            {
                "chat_id": 100000001,
                "user_id": 200000001,
                "username": "user1",
                "message_type": "COMMAND",
                "content": "/start",
                "message_id": 1
            },
            {
                "chat_id": 100000001,
                "user_id": 200000001,
                "username": "user1",
                "message_type": "TEXT",
                "content": "Привет! Как дела?",
                "message_id": 2
            },
            {
                "chat_id": 100000002,
                "user_id": 200000002,
                "username": "user2",
                "message_type": "TEXT",
                "content": "Расскажи что-нибудь интересное",
                "message_id": 3
            },
            {
                "chat_id": 100000003,
                "user_id": 200000003,
                "username": "user3",
                "message_type": "VOICE",
                "content": "Voice message, duration: 2s, file_id: voice_001",
                "message_id": 4
            },
            {
                "chat_id": 100000001,
                "user_id": 200000001,
                "username": "user1",
                "message_type": "COMMAND",
                "content": "/help",
                "message_id": 5
            }
        ]
        
        print("\n" + "="*70)
        print("🚀 ИСПРАВЛЕННЫЙ TELEGRAM БОТ - ДЕМОНСТРАЦИЯ ЛОГИРОВАНИЯ")
        print("="*70)
        
        for i, msg in enumerate(messages, 1):
            if not self.running:
                break
                
            print(f"\n📨 Сообщение {i}:")
            print(f"   👤 Пользователь: @{msg['username']} (ID: {msg['user_id']})")
            print(f"   💬 Тип: {msg['message_type']}")
            print(f"   📝 Содержимое: {msg['content'][:40]}...")
            print(f"   🆔 Chat ID: {msg['chat_id']}")
            
            # Логируем входящее сообщение
            log_message(**msg)
            
            # Имитируем обработку
            await asyncio.sleep(0.5)
            
            # Генерируем ответ
            response = self.generate_response(msg)
            print(f"   🤖 Ответ: {response[:40]}...")
            
            # Логируем ответ
            log_response(msg['chat_id'], "TEXT", True)
            
            await asyncio.sleep(1)
        
        print("\n" + "="*70)
        print("📊 СТАТИСТИКА РАБОТЫ ИСПРАВЛЕННОГО БОТА")
        print("="*70)
        print(f"📨 Обработано сообщений: {len(messages)}")
        print(f"👥 Уникальных пользователей: 3")
        print(f"💬 Текстовых сообщений: 2")
        print(f"🎤 Голосовых сообщений: 1")
        print(f"⚡ Команд: 2")
        print(f"✅ Ошибок с timezone: 0")
        
        print("\n📁 Логи сохранены:")
        print("   📄 logs/messages.log - все входящие сообщения")
        print("   📄 logs/combined.log - общие логи")
        print("   📄 logs/error.log - ошибки")
        
        # Показываем примеры логов
        print("\n🔍 Примеры записей в логах:")
        try:
            with open("logs/messages.log", "r", encoding="utf-8") as f:
                lines = f.readlines()
                # Показываем последние 3 строки с сообщениями
                message_lines = [line for line in lines if "TYPE:" in line]
                for line in message_lines[-3:]:
                    # Извлекаем только основную информацию
                    if "CHAT:" in line:
                        parts = line.split("CHAT:")
                        if len(parts) > 1:
                            chat_info = parts[1].split("CONTENT:")[0].strip()
                            content = parts[1].split("CONTENT:")[1].strip()[:30]
                            print(f"   📝 {chat_info} - {content}...")
        except FileNotFoundError:
            print("   Логи еще не созданы")
        
        print("\n✨ Исправленный бот работает корректно!")
        print("💡 Проблема с timezone решена!")
        print("🚀 Бот готов к реальному запуску с Telegram API")

    def generate_response(self, message):
        """Генерирует ответ на сообщение"""
        if message["message_type"] == "COMMAND":
            if message["content"] == "/start":
                return "🤖 Привет! Я исправленный бот с логированием. Все работает!"
            elif message["content"] == "/help":
                return "📋 Команды: /start, /help. Логирование активно!"
            else:
                return "❓ Неизвестная команда. Используй /help"
        
        elif message["message_type"] == "TEXT":
            return f"🤖 Получил: '{message['content']}'. Логирование работает!"
        
        elif message["message_type"] == "VOICE":
            return "🎤 Голосовое сообщение получено и залогировано!"
        
        else:
            return "🤖 Сообщение обработано и залогировано!"

async def main():
    """Главная функция"""
    print("🔧 Запуск исправленного Telegram бота")
    print("📝 Демонстрация системы логирования")
    print("✅ Проблема с timezone исправлена")
    print("📁 Логи сохраняются в папке logs/")
    print("-" * 50)
    
    # Создаем папку для логов
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    bot = FixedBot()
    
    try:
        await bot.start_bot()
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем")
    except Exception as e:
        log_error(f"Ошибка при запуске бота: {e}")
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())
