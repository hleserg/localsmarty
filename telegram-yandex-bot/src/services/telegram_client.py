from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import logging
import os

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramClient:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.updater = Updater(self.token, use_context=True)

    def start(self, update: Update, context: CallbackContext) -> None:
        update.message.reply_text('Привет! Я бот, который использует Яндекс GPT.')

    def run(self):
        dp = self.updater.dispatcher
        dp.add_handler(CommandHandler("start", self.start))

        logger.info("Бот запущен.")
        self.updater.start_polling()
        self.updater.idle()