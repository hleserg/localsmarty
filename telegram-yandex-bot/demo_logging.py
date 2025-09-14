#!/usr/bin/env python3
"""
Демонстрация системы логирования сообщений
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Добавляем src в путь Python
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from utils.logger import log_message, log_response, log_info, log_error

def demo_logging():
    """Демонстрация логирования сообщений"""
    print("🤖 Демонстрация системы логирования Telegram бота")
    print("📝 Показываем, как будут логироваться входящие сообщения")
    print("-" * 60)
    
    # Создаем папку для логов
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Демонстрируем различные типы сообщений
    demo_messages = [
        {
            "chat_id": 123456789,
            "user_id": 987654321,
            "username": "test_user",
            "message_type": "COMMAND",
            "content": "/start",
            "message_id": 1
        },
        {
            "chat_id": 123456789,
            "user_id": 987654321,
            "username": "test_user",
            "message_type": "TEXT",
            "content": "Привет! Как дела?",
            "message_id": 2
        },
        {
            "chat_id": 123456789,
            "user_id": 987654321,
            "username": "test_user",
            "message_type": "TEXT",
            "content": "Расскажи мне что-нибудь интересное про искусственный интеллект",
            "message_id": 3
        },
        {
            "chat_id": 123456789,
            "user_id": 987654321,
            "username": "test_user",
            "message_type": "VOICE",
            "content": "Voice message, duration: 5s, file_id: BAADBAADrwADBREAAYag",
            "message_id": 4
        },
        {
            "chat_id": 123456789,
            "user_id": 987654321,
            "username": "test_user",
            "message_type": "COMMAND",
            "content": "/help",
            "message_id": 5
        }
    ]
    
    print("📨 Логируем входящие сообщения:")
    for msg in demo_messages:
        log_message(**msg)
        print(f"   ✅ Сообщение {msg['message_id']}: {msg['message_type']} - {msg['content'][:30]}...")
    
    print("\n📤 Логируем ответы бота:")
    responses = [
        {"chat_id": 123456789, "response_type": "TEXT", "success": True},
        {"chat_id": 123456789, "response_type": "TEXT", "success": True},
        {"chat_id": 123456789, "response_type": "TEXT", "success": True},
        {"chat_id": 123456789, "response_type": "TEXT", "success": True},
        {"chat_id": 123456789, "response_type": "TEXT", "success": True},
    ]
    
    for i, resp in enumerate(responses, 1):
        log_response(**resp)
        print(f"   ✅ Ответ {i}: {resp['response_type']} - SUCCESS")
    
    print("\n📁 Логи сохранены в файлы:")
    print(f"   📄 logs/messages.log - {len(demo_messages)} входящих сообщений")
    print(f"   📄 logs/combined.log - Общие логи приложения")
    print(f"   📄 logs/error.log - Логи ошибок")
    
    print("\n🔍 Пример содержимого logs/messages.log:")
    try:
        with open("logs/messages.log", "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines[-3:]:  # Показываем последние 3 строки
                print(f"   {line.strip()}")
    except FileNotFoundError:
        print("   Файл логов еще не создан")
    
    print("\n✨ Демонстрация завершена!")
    print("💡 Для реального запуска бота:")
    print("   1. Получите токен бота от @BotFather в Telegram")
    print("   2. Настройте Yandex Cloud API")
    print("   3. Заполните файл .env реальными данными")
    print("   4. Запустите: python run_local.py")

if __name__ == "__main__":
    demo_logging()
