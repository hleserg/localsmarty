#!/usr/bin/env python3
"""
Скрипт для установки webhook через прямой HTTP запрос к Telegram API
"""

import requests
import json
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

def set_webhook():
    """Установка webhook через прямой HTTP запрос"""
    
    # Получаем токен и URL из переменных окружения
    token = os.getenv("TELEGRAM_TOKEN")
    webhook_url = os.getenv("WEBHOOK_URL", "https://talkbot.skhlebnikov.ru")
    webhook_path = os.getenv("WEBHOOK_PATH", "/bot")
    secret_token = os.getenv("WEBHOOK_SECRET_TOKEN")
    
    if not token:
        print("❌ TELEGRAM_TOKEN не установлен в .env файле")
        return False
    
    # Формируем полный URL webhook
    full_webhook_url = f"{webhook_url}{webhook_path}"
    
    # Параметры для allowed_updates
    allowed_updates = [
        "message",
        "edited_message", 
        "business_connection",
        "business_message",
        "edited_business_message",
        "deleted_business_messages"
    ]
    
    # URL для установки webhook
    api_url = f"https://api.telegram.org/bot{token}/setWebhook"
    
    # Параметры запроса
    params = {
        "url": full_webhook_url,
        "allowed_updates": json.dumps(allowed_updates)
    }
    
    # Добавляем secret_token если он есть
    if secret_token:
        params["secret_token"] = secret_token
    
    print(f"🔗 Устанавливаем webhook: {full_webhook_url}")
    print(f"📋 Allowed updates: {allowed_updates}")
    
    try:
        # Отправляем запрос
        response = requests.post(api_url, params=params, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                print("✅ Webhook успешно установлен!")
                print(f"📊 Результат: {result.get('description', 'OK')}")
                return True
            else:
                print(f"❌ Ошибка установки webhook: {result.get('description', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP ошибка {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка запроса: {e}")
        return False

def delete_webhook():
    """Удаление webhook"""
    
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        print("❌ TELEGRAM_TOKEN не установлен в .env файле")
        return False
    
    api_url = f"https://api.telegram.org/bot{token}/deleteWebhook"
    
    print("🗑️ Удаляем старый webhook...")
    
    try:
        response = requests.post(api_url, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                print("✅ Webhook успешно удален!")
                return True
            else:
                print(f"❌ Ошибка удаления webhook: {result.get('description', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP ошибка {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка запроса: {e}")
        return False

def get_webhook_info():
    """Получение информации о текущем webhook"""
    
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        print("❌ TELEGRAM_TOKEN не установлен в .env файле")
        return False
    
    api_url = f"https://api.telegram.org/bot{token}/getWebhookInfo"
    
    print("📊 Получаем информацию о webhook...")
    
    try:
        response = requests.get(api_url, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                webhook_info = result.get("result", {})
                print("✅ Информация о webhook:")
                print(f"   URL: {webhook_info.get('url', 'Не установлен')}")
                print(f"   Has custom certificate: {webhook_info.get('has_custom_certificate', False)}")
                print(f"   Pending update count: {webhook_info.get('pending_update_count', 0)}")
                print(f"   Last error date: {webhook_info.get('last_error_date', 'Нет')}")
                print(f"   Last error message: {webhook_info.get('last_error_message', 'Нет')}")
                print(f"   Max connections: {webhook_info.get('max_connections', 'Не установлено')}")
                print(f"   Allowed updates: {webhook_info.get('allowed_updates', [])}")
                return True
            else:
                print(f"❌ Ошибка получения информации: {result.get('description', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP ошибка {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка запроса: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "set":
            set_webhook()
        elif command == "delete":
            delete_webhook()
        elif command == "info":
            get_webhook_info()
        else:
            print("❌ Неизвестная команда. Используйте: set, delete, info")
    else:
        print("🤖 Управление webhook для Telegram бота")
        print("")
        print("Использование:")
        print("  python set_webhook.py set     - Установить webhook")
        print("  python set_webhook.py delete  - Удалить webhook")
        print("  python set_webhook.py info    - Показать информацию о webhook")
        print("")
        print("Убедитесь, что файл .env содержит:")
        print("  TELEGRAM_TOKEN=your_bot_token")
        print("  WEBHOOK_URL=https://talkbot.skhlebnikov.ru")
        print("  WEBHOOK_PATH=/bot")
        print("  WEBHOOK_SECRET_TOKEN=your_secret_token")
