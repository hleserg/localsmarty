import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from services.yandex_client import get_gpt_response
from dotenv import load_dotenv

load_dotenv()

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Получение токена из переменных окружения
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Я бот, использующий Яндекс GPT. Как я могу помочь?')

def handle_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    logger.info(f"Received message: {user_message}")
    
    # Получение ответа от Яндекс GPT
    gpt_response = get_gpt_response(user_message)
    update.message.reply_text(gpt_response)

def main() -> None:
    updater = Updater(TELEGRAM_TOKEN)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    logger.info("Бот запущен.")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()