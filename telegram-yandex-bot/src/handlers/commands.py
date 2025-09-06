from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from services.yandex_client import get_gpt_response

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Я ваш бот, как я могу помочь?')

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Доступные команды:\n/start - Начать общение\n/help - Получить помощь')

def chat_with_gpt(update: Update, context: CallbackContext) -> None:
    user_message = ' '.join(context.args)
    if user_message:
        response = get_gpt_response(user_message)
        update.message.reply_text(response)
    else:
        update.message.reply_text('Пожалуйста, введите сообщение для отправки в GPT.')