#!/usr/bin/env python3
"""
Тестовый скрипт для локального тестирования webhook
"""

import requests
import json

def test_local_webhook():
    """Тестирование локального webhook"""
    
    # URL локального webhook
    webhook_url = "http://localhost:11844/bot"
    
    # Тестовые данные
    test_data = {
        "update_id": 123,
        "business_message": {
            "business_connection_id": "test123",
            "text": "test message",
            "chat": {
                "id": 123,
                "type": "private"
            },
            "from": {
                "id": 123,
                "first_name": "Test",
                "is_bot": False
            },
            "message_id": 1,
            "date": 1234567890
        }
    }
    
    print(f"🧪 Тестирование локального webhook: {webhook_url}")
    print(f"📊 Данные: {json.dumps(test_data, indent=2)}")
    
    try:
        # Отправляем POST запрос
        response = requests.post(
            webhook_url,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📡 Статус ответа: {response.status_code}")
        print(f"📝 Ответ: {response.text}")
        
        if response.status_code == 200:
            print("✅ Локальный webhook работает!")
        else:
            print("❌ Локальный webhook не работает")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    test_local_webhook()
