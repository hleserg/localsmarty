import logging
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any

# Создаем директорию для логов если её нет
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, "error.log"), mode='a', encoding='utf-8'),
        logging.FileHandler(os.path.join(log_dir, "combined.log"), mode='a', encoding='utf-8'),
        logging.FileHandler(os.path.join(log_dir, "messages.log"), mode='a', encoding='utf-8'),
        logging.FileHandler(os.path.join(log_dir, "updates.json"), mode='a', encoding='utf-8'),
        logging.StreamHandler()  # Вывод в консоль
    ]
)

# Настройка консольного вывода для лучшей читаемости
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

# Добавляем консольный обработчик к корневому логгеру
root_logger = logging.getLogger()
root_logger.addHandler(console_handler)

logger = logging.getLogger(__name__)

def log_info(message: str):
    logger.info(message)

def log_error(message: str):
    logger.error(message)

def log_message(chat_id: int, user_id: int, username: Optional[str], message_type: str, content: str, message_id: Optional[int] = None):
    """Логирует входящее сообщение с подробной информацией"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    username_str = f"@{username}" if username else "Unknown"
    
    log_entry = (
        f"[{timestamp}] CHAT:{chat_id} USER:{user_id} ({username_str}) "
        f"TYPE:{message_type} ID:{message_id} CONTENT:{content[:200]}"
    )
    
    # Краткая информация для консоли
    console_entry = f"💬 {message_type} from {username_str} in chat {chat_id}: {content[:50]}{'...' if len(content) > 50 else ''}"
    
    # Логируем в общий лог
    logger.info(log_entry)
    
    # Выводим краткую информацию в консоль
    print(f"🔄 {console_entry}")
    
    # Создаем отдельный логгер для сообщений
    message_logger = logging.getLogger("messages")
    message_logger.info(log_entry)

def log_response(chat_id: int, response_type: str, success: bool, error_msg: Optional[str] = None):
    """Логирует отправку ответа"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "SUCCESS" if success else "ERROR"
    
    log_entry = f"[{timestamp}] CHAT:{chat_id} RESPONSE:{response_type} STATUS:{status}"
    if error_msg:
        log_entry += f" ERROR:{error_msg}"
    
    # Краткая информация для консоли
    status_emoji = "✅" if success else "❌"
    console_entry = f"{status_emoji} Response {response_type} to chat {chat_id}: {status}"
    if error_msg:
        console_entry += f" - {error_msg}"
    
    logger.info(log_entry)
    
    # Выводим краткую информацию в консоль
    print(f"🤖 {console_entry}")

def log_update_json(update_data: Dict[str, Any]):
    """Логирует полный JSON входящего update"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Создаем структуру для логирования
    log_entry = {
        "timestamp": timestamp,
        "update": update_data
    }
    
    # Конвертируем в JSON с красивым форматированием
    json_str = json.dumps(log_entry, ensure_ascii=False, indent=2)
    
    # Логируем в отдельный файл для JSON updates
    update_logger = logging.getLogger("updates")
    update_logger.info(f"\n{'='*80}\n{json_str}\n{'='*80}")
    
    # Логируем краткую информацию в консоль
    update_id = update_data.get("update_id", "unknown")
    
    # Определяем тип update для консоли
    update_type = "UNKNOWN"
    if "message" in update_data:
        if "text" in update_data["message"]:
            update_type = "TEXT"
        elif "voice" in update_data["message"]:
            update_type = "VOICE"
        elif "photo" in update_data["message"]:
            update_type = "PHOTO"
        else:
            update_type = "MESSAGE"
    elif "callback_query" in update_data:
        update_type = "CALLBACK"
    elif "edited_message" in update_data:
        update_type = "EDITED"
    
    # Получаем информацию о пользователе
    user_info = "Unknown"
    if "message" in update_data:
        from_user = update_data["message"].get("from", {})
        username = from_user.get("username")
        first_name = from_user.get("first_name", "")
        if username:
            user_info = f"@{username}"
        elif first_name:
            user_info = first_name
    elif "callback_query" in update_data:
        from_user = update_data["callback_query"].get("from", {})
        username = from_user.get("username")
        first_name = from_user.get("first_name", "")
        if username:
            user_info = f"@{username}"
        elif first_name:
            user_info = first_name
    
    # Выводим краткую информацию в консоль
    console_message = f"📨 UPDATE_ID:{update_id} TYPE:{update_type} USER:{user_info}"
    
    # Добавляем содержимое для текстовых сообщений
    if update_type == "TEXT" and "message" in update_data:
        text_content = update_data["message"].get("text", "")[:50]
        if len(text_content) > 50:
            text_content += "..."
        console_message += f" CONTENT:{text_content}"
    
    logger.info(console_message)