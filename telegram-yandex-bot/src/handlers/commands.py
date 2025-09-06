from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from services.yandex_client import get_gpt_response
import logging

logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /start"""
    welcome_message = (
        "🤖 Привет! Я ваш AI-помощник на базе Yandex GPT.\n\n"
        "Просто отправьте мне сообщение, и я отвечу с помощью "
        "искусственного интеллекта!\n\n"
        "Используйте /help для получения дополнительной информации."
    )
    update.message.reply_text(welcome_message)

def help_command(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /help"""
    help_message = (
        "📖 Доступные команды:\n\n"
        "/start - Начать общение с ботом\n"
        "/help - Показать эту справку\n"
        "/chat <сообщение> - Отправить сообщение в GPT\n\n"
        "💡 Вы также можете просто написать сообщение без команды!\n\n"
        "⚙️ Технические детали:\n"
        "• Используется Yandex Foundation Models\n"
        "• Максимальная длина сообщения: 4000 символов\n"
        "• Время ответа: до 30 секунд"
    )
    update.message.reply_text(help_message)

def chat_with_gpt(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /chat для отправки сообщения в GPT"""
    user_message = ' '.join(context.args)
    
    if not user_message:
        update.message.reply_text(
            "❌ Пожалуйста, введите сообщение после команды /chat\n"
            "Пример: /chat Расскажи анекдот"
        )
        return
    
    if len(user_message) > 4000:
        update.message.reply_text(
            "❌ Сообщение слишком длинное. Максимум 4000 символов."
        )
        return
    
    try:
        # Показываем, что бот печатает
        context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
        
        # Получаем ответ от GPT
        response = get_gpt_response(user_message)
        
        # Отправляем ответ (с разбивкой на части, если нужно)
        if len(response) > 4096:
            for i in range(0, len(response), 4096):
                chunk = response[i:i+4096]
                update.message.reply_text(chunk)
        else:
            update.message.reply_text(response)
            
        logger.info(f"Successfully processed /chat command for user {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"Error in chat_with_gpt: {e}")
        update.message.reply_text(
            "😔 Произошла ошибка при обработке запроса. Попробуйте еще раз."
        )