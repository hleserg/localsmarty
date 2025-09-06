import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from utils.markdown import transform_to_markdown_v2
from services.yandex_client import get_gpt_response
from config import config
from telegram.error import BadRequest

logger = logging.getLogger(__name__)


async def _reply_md_v2_safe(update: Update, text: str, disable_preview: bool = True) -> None:
    """Reply with MarkdownV2; on BadRequest fallback to plain text."""
    if not update.message:
        return
    try:
        await update.message.reply_text(
            transform_to_markdown_v2(text),
            parse_mode=ParseMode.MARKDOWN_V2,
            disable_web_page_preview=disable_preview,
        )
    except BadRequest as e:
        # Fallback to plain text if MarkdownV2 fails
        logging.getLogger(__name__).warning(f"MarkdownV2 failed, fallback to plain: {e}")
        await update.message.reply_text(text, disable_web_page_preview=disable_preview)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for /start command"""
    welcome_message = (
        "🤖 Привет! Я бот с интеграцией YandexGPT.\n\n"
        "Просто отправьте мне сообщение, и я отвечу с помощью искусственного интеллекта.\n"
        f"Контекст диалога: {'включен' if config.ENABLE_CONTEXT else 'отключен'}\n"
        f"Голосовые сообщения: {'поддерживаются' if config.ENABLE_VOICE else 'не поддерживаются'}\n\n"
        "Используйте /help для получения списка команд."
    )
    if update.message:
        await _reply_md_v2_safe(update, welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
    
    if update.message:
        await _reply_md_v2_safe(update, help_text)

async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for /ping command - bot health check"""
    ping_message = (
        "🏓 Pong!\n"
        f"Бот работает нормально.\n"
        f"Версия: 1.0.0\n"
        f"YandexGPT: {'✅ настроен' if config.YC_FOLDER_ID and (config.YC_API_KEY or config.YC_IAM_TOKEN or config.YC_SA_KEY_FILE or config.YC_SA_KEY_JSON) else '❌ не настроен'}\n"
        f"Голосовые функции: {'✅ включены' if config.ENABLE_VOICE else '❌ отключены'}"
    )
    if update.message:
        await _reply_md_v2_safe(update, ping_message)

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for regular text messages"""
    if not update.message:
        return
    user_message = update.message.text or ""
    chat_id = update.effective_chat.id if update.effective_chat else 0

    logger.info(f"Received text message from chat {chat_id}: {user_message[:50]}...")

    try:
        # Get response from YandexGPT
        gpt_response = get_gpt_response(user_message, chat_id)
        await _reply_md_v2_safe(update, gpt_response)
        logger.info(f"Sent response to chat {chat_id}")
    except Exception as e:
        logger.error(f"Error handling text message for chat {chat_id}: {str(e)}")
        await _reply_md_v2_safe(update, "Извините, произошла ошибка при обработке вашего сообщения. Попробуйте позже.")