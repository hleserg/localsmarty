#!/usr/bin/env python3
"""
Тестовая версия бота для локального запуска с демонстрацией логирования
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

class MockTelegramBot:
    """Мок-версия Telegram бота для демонстрации логирования"""
    
    def __init__(self):
        self.running = False
        self.message_count = 0
        
    async def start_polling(self):
        """Имитация polling с демонстрацией логирования"""
        log_info("🤖 Тестовый бот запущен!")
        log_info("📝 Система логирования активна")
        log_info("💡 Отправьте сообщения для демонстрации логирования")
        log_info("🛑 Нажмите Ctrl+C для остановки")
        
        self.running = True
        
        # Демонстрируем различные типы сообщений
        demo_messages = [
            {
                "chat_id": 123456789,
                "user_id": 987654321,
                "username": "demo_user",
                "message_type": "COMMAND",
                "content": "/start",
                "message_id": 1
            },
            {
                "chat_id": 123456789,
                "user_id": 987654321,
                "username": "demo_user",
                "message_type": "TEXT",
                "content": "Привет! Как дела?",
                "message_id": 2
            },
            {
                "chat_id": 123456789,
                "user_id": 987654321,
                "username": "demo_user",
                "message_type": "TEXT",
                "content": "Расскажи мне что-нибудь интересное",
                "message_id": 3
            },
            {
                "chat_id": 123456789,
                "user_id": 987654321,
                "username": "demo_user",
                "message_type": "COMMAND",
                "content": "/help",
                "message_id": 4
            },
            {
                "chat_id": 123456789,
                "user_id": 987654321,
                "username": "demo_user",
                "message_type": "VOICE",
                "content": "Voice message, duration: 3s, file_id: demo_voice_123",
                "message_id": 5
            }
        ]
        
        print("\n" + "="*60)
        print("📨 ДЕМОНСТРАЦИЯ ЛОГИРОВАНИЯ ВХОДЯЩИХ СООБЩЕНИЙ")
        print("="*60)
        
        for i, msg in enumerate(demo_messages, 1):
            if not self.running:
                break
                
            print(f"\n📩 Сообщение {i}: {msg['message_type']} - {msg['content'][:30]}...")
            
            # Логируем входящее сообщение
            log_message(**msg)
            
            # Имитируем обработку
            await asyncio.sleep(1)
            
            # Логируем ответ
            log_response(msg['chat_id'], "TEXT", True)
            print(f"✅ Ответ отправлен")
            
            await asyncio.sleep(2)
        
        print("\n" + "="*60)
        print("📊 СТАТИСТИКА ЛОГИРОВАНИЯ")
        print("="*60)
        print(f"📨 Обработано сообщений: {len(demo_messages)}")
        print(f"📁 Логи сохранены в папку: logs/")
        print(f"📄 messages.log - входящие сообщения")
        print(f"📄 combined.log - общие логи")
        print(f"📄 error.log - ошибки")
        
        print("\n🔍 Последние записи в логах:")
        try:
            with open("logs/messages.log", "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines[-3:]:
                    print(f"   {line.strip()}")
        except FileNotFoundError:
            print("   Логи еще не созданы")
        
        print("\n✨ Демонстрация завершена!")
        print("💡 Для реального запуска:")
        print("   1. Получите токен от @BotFather")
        print("   2. Настройте Yandex Cloud API")
        print("   3. Заполните .env файл")
        print("   4. Запустите: python run_local.py")

async def main():
    """Главная функция"""
    print("🤖 Запуск тестового Telegram бота")
    print("📝 Демонстрация системы логирования")
    print("📁 Логи сохраняются в папке logs/")
    print("-" * 50)
    
    # Создаем папку для логов
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    bot = MockTelegramBot()
    
    try:
        await bot.start_polling()
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем")
    except Exception as e:
        log_error(f"Ошибка при запуске бота: {e}")
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())
