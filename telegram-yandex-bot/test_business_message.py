#!/usr/bin/env python3
"""
Тестовый скрипт для проверки обработки business_message
"""

import json
import asyncio
from telegram import Update
from telegram.ext import Application

async def test_business_message():
    """Тестирование business_message"""
    
    # Пример данных business_message
    test_data = {
        "update_id": 240051469,
        "business_message": {
            "business_connection_id": "o1z9umxS4UmeDwAAMz5UekAA75o",
            "channel_chat_created": False,
            "delete_chat_photo": False,
            "group_chat_created": False,
            "supergroup_chat_created": False,
            "text": "Привет сережа",
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
    
    print("🧪 Тестирование business_message...")
    print(f"📊 Данные: {json.dumps(test_data, indent=2)}")
    
    try:
        # Создаем Update объект
        update = Update.de_json(test_data, None)
        
        print(f"✅ Update создан: {update}")
        print(f"📝 Update ID: {update.update_id}")
        
        # Проверяем business_message
        if update.business_message:
            print("✅ business_message найден!")
            print(f"📝 Текст: {update.business_message.text}")
            print(f"👤 От: {update.business_message.from_user.first_name}")
            print(f"💬 Чат: {update.business_message.chat.id}")
            print(f"🔗 Business Connection ID: {update.business_message.business_connection_id}")
        else:
            print("❌ business_message не найден")
            
        # Проверяем обычное сообщение
        if update.message:
            print("✅ message найден!")
        else:
            print("❌ message не найден")
            
        # Проверяем effective_chat и effective_user
        if update.effective_chat:
            print(f"✅ effective_chat: {update.effective_chat.id}")
        else:
            print("❌ effective_chat не найден")
            
        if update.effective_user:
            print(f"✅ effective_user: {update.effective_user.first_name}")
        else:
            print("❌ effective_user не найден")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_business_message())
