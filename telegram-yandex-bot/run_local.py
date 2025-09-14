#!/usr/bin/env python3
"""
Скрипт для локального запуска Telegram бота с YandexGPT
"""

import os
import sys
from pathlib import Path

# Добавляем src в путь Python
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def main():
    """Запуск бота"""
    print("🤖 Запуск Telegram бота с YandexGPT...")
    print("📝 Логирование всех входящих сообщений включено")
    print("📁 Логи сохраняются в папке logs/")
    print("-" * 50)
    
    # Проверяем наличие .env файла
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        print("⚠️  Файл .env не найден!")
        print("📋 Скопируйте env.example в .env и заполните переменные:")
        print("   cp env.example .env")
        print("   # Затем отредактируйте .env файл")
        return
    
    # Проверяем переменные окружения
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ["TELEGRAM_TOKEN", "YC_FOLDER_ID"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Отсутствуют обязательные переменные окружения:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n📝 Проверьте файл .env")
        return
    
    # Запускаем бота
    try:
        from bot import main as bot_main
        bot_main()
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка при запуске бота: {e}")
        return

if __name__ == "__main__":
    main()
