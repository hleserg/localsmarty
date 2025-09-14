#!/usr/bin/env python3
"""
Тестирование business контекста с реалистичным сообщением
"""

import requests
import json

def test_business_context():
    """Тестирование business контекста"""
    
    # Реалистичные данные business_message
    test_data = {
        "update_id": 123,
        "business_message": {
            "business_connection_id": "test123",
            "text": "Привет! Мне нужна помощь с проектом. Можете ли вы помочь?",
            "chat": {
                "id": 123,
                "type": "private"
            },
            "from": {
                "id": 123,
                "first_name": "Анна",
                "is_bot": False
            },
            "message_id": 1,
            "date": 1234567890
        }
    }
    
    print("🧪 Тестирование business контекста")
    print(f"📊 Сообщение: {test_data['business_message']['text']}")
    print(f"👤 От: {test_data['business_message']['from']['first_name']}")
    
    try:
        response = requests.post(
            "http://localhost:11844/bot",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📡 Статус ответа: {response.status_code}")
        print(f"📝 Ответ: {response.text}")
        
        if response.status_code == 200:
            print("✅ Business контекст работает!")
        else:
            print("❌ Ошибка в business контексте")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    test_business_context()
