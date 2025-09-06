import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from services.yandex_client import get_gpt_response
from dotenv import load_dotenv

load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO'))
)
logger = logging.getLogger(__name__)

# Получение токена из переменных окружения
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN environment variable is required")

def start(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /start"""
    welcome_message = (
        "🤖 Привет! Я бот, использующий Yandex GPT для общения.\n\n"
        "Просто отправьте мне любое сообщение, и я отвечу с помощью "
        "искусственного интеллекта от Яндекса!\n\n"
        "Доступные команды:\n"
        "/start - показать это сообщение\n"
        "/help - получить помощь"
    )
    update.message.reply_text(welcome_message)

def help_command(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /help"""
    help_message = (
        "📖 Помощь:\n\n"
        "Этот бот использует Yandex GPT для ответа на ваши вопросы.\n\n"
        "🔹 Просто напишите любое сообщение\n"
        "🔹 Бот ответит с помощью AI\n"
        "🔹 Поддерживается русский и английский языки\n\n"
        "Команды:\n"
        "/start - начать работу с ботом\n"
        "/help - показать эту справку\n\n"
        "⚠️ Обратите внимание: ответ может занять несколько секунд."
    )
    update.message.reply_text(help_message)

def handle_message(update: Update, context: CallbackContext) -> None:
    """Обработчик текстовых сообщений"""
    user_message = update.message.text
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    
    logger.info(f"Received message from user {username} (ID: {user_id}): {user_message[:100]}...")
    
    # Проверка длины сообщения
    if len(user_message) > 4000:
        update.message.reply_text(
            "❌ Сообщение слишком длинное. Пожалуйста, сократите его до 4000 символов."
        )
        return
    
    # Отправка индикатора "печатает..."
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    
    try:
        # Получение ответа от Яндекс GPT
        gpt_response = get_gpt_response(user_message)
        
        # Проверка длины ответа для Telegram (максимум 4096 символов)
        if len(gpt_response) > 4096:
            # Разбиваем длинный ответ на части
            for i in range(0, len(gpt_response), 4096):
                chunk = gpt_response[i:i+4096]
                update.message.reply_text(chunk)
        else:
            update.message.reply_text(gpt_response)
            
        logger.info(f"Sent response to user {username} (ID: {user_id})")
        
    except Exception as e:
        logger.error(f"Error processing message from user {username} (ID: {user_id}): {e}")
        error_message = (
            "😔 Извините, произошла ошибка при обработке вашего сообщения. "
            "Пожалуйста, попробуйте еще раз через несколько минут."
        )
        update.message.reply_text(error_message)

def error_handler(update: Update, context: CallbackContext) -> None:
    """Обработчик ошибок"""
    logger.error(f"Update {update} caused error {context.error}")

def main() -> None:
    """Главная функция запуска бота"""
    try:
        # Создание Updater и передача ему токена бота
        updater = Updater(TELEGRAM_TOKEN)

        # Получение диспетчера для регистрации обработчиков
        dispatcher = updater.dispatcher

        # Регистрация обработчиков команд
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("help", help_command))
        
        # Регистрация обработчика текстовых сообщений
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
        
        # Регистрация обработчика ошибок
        dispatcher.add_error_handler(error_handler)

        logger.info("🚀 Telegram бот запущен и готов к работе!")
        
        # Запуск бота
        updater.start_polling()
        
        # Бот работает до нажатия Ctrl-C
        updater.idle()
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == '__main__':
    main()