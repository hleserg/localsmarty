import logging
from telegram import Update
from telegram.ext import CallbackContext
from services.yandex_client import get_gpt_response
from config import config

logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext) -> None:
    """Handler for /start command"""
    welcome_message = (
        "🤖 Привет! Я бот с интеграцией YandexGPT.\n\n"
        "Просто отправьте мне сообщение, и я отвечу с помощью искусственного интеллекта.\n"
        f"Контекст диалога: {'включен' if config.ENABLE_CONTEXT else 'отключен'}\n"
        f"Голосовые сообщения: {'поддерживаются' if config.ENABLE_VOICE else 'не поддерживаются'}\n\n"
        "Используйте /help для получения списка команд."
    )
    update.message.reply_text(welcome_message)

def help_command(update: Update, context: CallbackContext) -> None:
    """Handler for /help command"""
    help_text = (
        "📋 *Доступные команды:*\n\n"
        "/start - Начать общение с ботом\n"
        "/help - Показать это сообщение\n"
        "/ping - Проверить работу бота\n\n"
        "💬 *Как использовать:*\n"
        "Просто отправьте текстовое сообщение, и я отвечу с помощью YandexGPT.\n"
    )
    
    if config.ENABLE_VOICE:
        help_text += "\n🎤 *Голосовые сообщения:*\nОтправьте голосовое сообщение, и я распознаю речь и отвечу."
    
    if config.ENABLE_CONTEXT:
        help_text += "\n🧠 *Контекст:*\nЯ помню предыдущие сообщения в рамках нашего диалога."
    
    update.message.reply_text(help_text, parse_mode='Markdown')

def ping_command(update: Update, context: CallbackContext) -> None:
    """Handler for /ping command - bot health check"""
    ping_message = (
        "🏓 Pong!\n"
        f"Бот работает нормально.\n"
        f"Версия: 1.0.0\n"
        f"YandexGPT: {'✅ настроен' if config.YC_FOLDER_ID and (config.YC_API_KEY or config.YC_IAM_TOKEN) else '❌ не настроен'}\n"
        f"Голосовые функции: {'✅ включены' if config.ENABLE_VOICE else '❌ отключены'}"
    )
    update.message.reply_text(ping_message)

def handle_text_message(update: Update, context: CallbackContext) -> None:
    """Handler for regular text messages"""
    user_message = update.message.text
    chat_id = update.effective_chat.id
    
    logger.info(f"Received text message from chat {chat_id}: {user_message[:50]}...")
    
    try:
        # Get response from YandexGPT
        gpt_response = get_gpt_response(user_message, chat_id)
        update.message.reply_text(gpt_response)
        logger.info(f"Sent response to chat {chat_id}")
        
    except Exception as e:
        logger.error(f"Error handling text message for chat {chat_id}: {str(e)}")
        update.message.reply_text(
            "Извините, произошла ошибка при обработке вашего сообщения. Попробуйте позже."
        )