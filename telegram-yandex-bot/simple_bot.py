#!/usr/bin/env python3
"""
Упрощенная версия бота для локального запуска
Работает с минимальными настройками и демонстрирует логирование
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

class SimpleBot:
    """Упрощенная версия бота с логированием"""
    
    def __init__(self):
        self.running = False
        
    async def simulate_telegram_messages(self):
        """Имитация получения сообщений от Telegram"""
        log_info("🤖 Простой бот запущен!")
        log_info("📝 Логирование всех сообщений активно")
        log_info("💬 Имитация работы с Telegram API")
        
        self.running = True
        
        # Имитируем различные типы сообщений
        messages = [
            {
                "chat_id": 111111111,
                "user_id": 222222222,
                "username": "alice",
                "message_type": "COMMAND",
                "content": "/start",
                "message_id": 101
            },
            {
                "chat_id": 111111111,
                "user_id": 222222222,
                "username": "alice",
                "message_type": "TEXT",
                "content": "Привет! Как дела?",
                "message_id": 102
            },
            {
                "chat_id": 333333333,
                "user_id": 444444444,
                "username": "bob",
                "message_type": "TEXT",
                "content": "Расскажи анекдот",
                "message_id": 201
            },
            {
                "chat_id": 555555555,
                "user_id": 666666666,
                "username": "charlie",
                "message_type": "VOICE",
                "content": "Voice message, duration: 4s, file_id: voice_abc123",
                "message_id": 301
            },
            {
                "chat_id": 111111111,
                "user_id": 222222222,
                "username": "alice",
                "message_type": "COMMAND",
                "content": "/help",
                "message_id": 103
            }
        ]
        
        print("\n" + "="*70)
        print("📱 ИМИТАЦИЯ РАБОТЫ TELEGRAM БОТА")
        print("="*70)
        
        for i, msg in enumerate(messages, 1):
            if not self.running:
                break
                
            print(f"\n📨 Получено сообщение {i}:")
            print(f"   👤 Пользователь: @{msg['username']} (ID: {msg['user_id']})")
            print(f"   💬 Тип: {msg['message_type']}")
            print(f"   📝 Содержимое: {msg['content'][:50]}...")
            print(f"   🆔 Chat ID: {msg['chat_id']}")
            
            # Логируем входящее сообщение
            log_message(**msg)
            
            # Имитируем обработку сообщения
            await asyncio.sleep(1)
            
            # Генерируем ответ
            response = self.generate_response(msg)
            print(f"   🤖 Ответ: {response[:50]}...")
            
            # Логируем ответ
            log_response(msg['chat_id'], "TEXT", True)
            
            await asyncio.sleep(2)
        
        print("\n" + "="*70)
        print("📊 СТАТИСТИКА РАБОТЫ БОТА")
        print("="*70)
        print(f"📨 Обработано сообщений: {len(messages)}")
        print(f"👥 Уникальных пользователей: 3")
        print(f"💬 Текстовых сообщений: 2")
        print(f"🎤 Голосовых сообщений: 1")
        print(f"⚡ Команд: 2")
        
        print("\n📁 Логи сохранены:")
        print("   📄 logs/messages.log - все входящие сообщения")
        print("   📄 logs/combined.log - общие логи")
        print("   📄 logs/error.log - ошибки")
        
        # Показываем примеры логов
        print("\n🔍 Примеры записей в логах:")
        try:
            with open("logs/messages.log", "r", encoding="utf-8") as f:
                lines = f.readlines()
                # Показываем последние 5 строк с сообщениями
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
        
        print("\n✨ Демонстрация завершена!")
        print("💡 Для реального запуска с Telegram API:")
        print("   1. Получите токен от @BotFather в Telegram")
        print("   2. Настройте Yandex Cloud API")
        print("   3. Заполните файл .env реальными данными")
        print("   4. Запустите: python run_local.py")

    def generate_response(self, message):
        """Генерирует ответ на сообщение"""
        if message["message_type"] == "COMMAND":
            if message["content"] == "/start":
                return "🤖 Привет! Я бот с интеграцией YandexGPT. Отправь мне сообщение!"
            elif message["content"] == "/help":
                return "📋 Доступные команды: /start, /help, /ping. Просто отправь текст!"
            else:
                return "❓ Неизвестная команда. Используй /help для справки."
        
        elif message["message_type"] == "TEXT":
            return f"🤖 Получил твое сообщение: '{message['content']}'. Это демо-режим!"
        
        elif message["message_type"] == "VOICE":
            return "🎤 Получил голосовое сообщение! В реальном режиме я бы его распознал."
        
        else:
            return "🤖 Получил сообщение неизвестного типа."

async def main():
    """Главная функция"""
    print("🚀 Запуск упрощенного Telegram бота")
    print("📝 Демонстрация системы логирования")
    print("📁 Логи сохраняются в папке logs/")
    print("-" * 50)
    
    # Создаем папку для логов
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    bot = SimpleBot()
    
    try:
        await bot.simulate_telegram_messages()
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем")
    except Exception as e:
        log_error(f"Ошибка при запуске бота: {e}")
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())
