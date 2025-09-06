#!/usr/bin/env python3
"""
Validation script for Telegram Yandex Bot
Проверяет корректность настройки и интеграции
"""

import os
import sys
sys.path.insert(0, 'src')

def validate_configuration():
    """Проверка конфигурации"""
    print("🔍 Проверка конфигурации...")
    
    required_vars = [
        'TELEGRAM_TOKEN',
        'YANDEX_API_KEY', 
        'YANDEX_FOLDER_ID'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Отсутствуют переменные окружения: {', '.join(missing_vars)}")
        print("💡 Создайте файл .env на основе .env.example")
        return False
    else:
        print("✅ Все необходимые переменные окружения установлены")
        return True

def validate_dependencies():
    """Проверка зависимостей"""
    print("\n📦 Проверка зависимостей...")
    
    try:
        import telegram
        import requests
        import pydantic
        from dotenv import load_dotenv
        print("✅ Все зависимости установлены")
        return True
    except ImportError as e:
        print(f"❌ Отсутствует зависимость: {e}")
        print("💡 Выполните: pip install -r requirements.txt")
        return False

def validate_imports():
    """Проверка импортов модулей бота"""
    print("\n🔧 Проверка модулей бота...")
    
    try:
        from services.yandex_client import YandexClient, get_gpt_response
        from config import config
        print("✅ Модули бота импортированы успешно")
        return True
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        return False

def validate_yandex_client():
    """Проверка клиента Yandex"""
    print("\n🤖 Проверка Yandex клиента...")
    
    # Устанавливаем тестовые переменные если реальных нет
    if not os.getenv('YANDEX_API_KEY'):
        os.environ['YANDEX_API_KEY'] = 'test-key'
        os.environ['YANDEX_FOLDER_ID'] = 'test-folder'
        print("⚠️  Используются тестовые данные (для реальной работы нужны настоящие ключи)")
    
    try:
        from services.yandex_client import YandexClient
        client = YandexClient()
        print("✅ YandexClient создан успешно")
        print(f"   📡 API URL: {client.api_url}")
        print(f"   🎯 Модель: {client.model}")
        return True
    except Exception as e:
        print(f"❌ Ошибка создания YandexClient: {e}")
        return False

def main():
    """Главная функция валидации"""
    print("🚀 Validation Script for Telegram Yandex Bot")
    print("=" * 50)
    
    # Загружаем переменные окружения
    from dotenv import load_dotenv
    load_dotenv()
    
    checks = [
        validate_dependencies(),
        validate_imports(),
        validate_yandex_client(),
        validate_configuration()
    ]
    
    print("\n" + "=" * 50)
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        print(f"🎉 Все проверки пройдены ({passed}/{total})")
        print("✅ Бот готов к запуску!")
        print("\n💡 Для запуска выполните:")
        print("   python src/bot.py")
    else:
        print(f"⚠️  Пройдено проверок: {passed}/{total}")
        print("❌ Необходимо исправить ошибки перед запуском")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)