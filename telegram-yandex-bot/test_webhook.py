#!/usr/bin/env python3
"""
Тестовый скрипт для проверки webhook
"""

import requests
import json

def test_webhook():
    """Тестирование webhook"""
    
    # URL webhook
    webhook_url = "https://talkbot.skhlebnikov.ru/bot"
    
    # Тестовые данные business_message
    test_data = {
        "update_id": 240051469,
        "business_message": {
            "business_connection_id": "o1z9umxS4UmeDwAAMz5UekAA75o",
            "channel_chat_created": False,
            "delete_chat_photo": False,
            "group_chat_created": False,
            "supergroup_chat_created": False,
            "text": "Тестовое сообщение",
            "chat": {
                "first_name": "Сергей",
                "id": 1111576171,
                "last_name": "Хлебников",
                "type": "private"
            },
            "date": 1757819859,
            "message_id": 374709,
            "from": {
                "first_name": "Сергей",
                "id": 1111576171,
                "is_bot": False,
                "language_code": "ru",
                "last_name": "Хлебников"
            }
        }
    }
    
    print(f"🧪 Тестирование webhook: {webhook_url}")
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
            print("✅ Webhook работает!")
        else:
            print("❌ Webhook не работает")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    test_webhook()
