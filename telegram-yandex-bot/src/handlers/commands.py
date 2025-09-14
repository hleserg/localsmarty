import logging
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatAction
from utils.markdown import transform_to_markdown_v2
from services.neuroapi_client import get_gpt_response
from config import config
from telegram.error import BadRequest
from utils.logger import log_message, log_response

logger = logging.getLogger(__name__)


async def _send_typing_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет статус 'печатает' для обычных сообщений"""
    if not update.message or not update.effective_chat:
        logger.warning("Cannot send typing status: missing message or chat")
        return
    try:
        logger.info(f"Sending typing status to chat {update.effective_chat.id}")
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        logger.info(f"Typing status sent successfully to chat {update.effective_chat.id}")
    except Exception as e:
        logger.error(f"Failed to send typing status: {e}")


async def _send_business_typing_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет статус 'печатает' для бизнес-сообщений"""
    if not update.business_message or not update.effective_chat:
        logger.warning("Cannot send business typing status: missing business_message or chat")
        return
    try:
        logger.info(f"Sending business typing status to chat {update.effective_chat.id}")
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        logger.info(f"Business typing status sent successfully to chat {update.effective_chat.id}")
    except Exception as e:
        logger.error(f"Failed to send business typing status: {e}")


async def _reply_md_v2_safe(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, disable_preview: bool = True) -> None:
    """Reply with MarkdownV2; on BadRequest fallback to plain text."""
    if not update.message or not update.effective_chat:
        return
    try:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=transform_to_markdown_v2(text),
            parse_mode=ParseMode.MARKDOWN_V2,
            disable_web_page_preview=disable_preview,
        )
    except BadRequest as e:
        # Fallback to plain text if MarkdownV2 fails
        logging.getLogger(__name__).warning(f"MarkdownV2 failed, fallback to plain: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            disable_web_page_preview=disable_preview,
        )

async def _reply_business_md_v2_safe(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, disable_preview: bool = True) -> None:
    """Reply to business message with MarkdownV2; on BadRequest fallback to plain text."""
    if not update.business_message or not update.effective_chat:
        return
    try:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=transform_to_markdown_v2(text),
            parse_mode=ParseMode.MARKDOWN_V2,
            disable_web_page_preview=disable_preview,
            business_connection_id=update.business_message.business_connection_id
        )
    except BadRequest as e:
        # Fallback to plain text if MarkdownV2 fails
        logging.getLogger(__name__).warning(f"MarkdownV2 failed for business message, fallback to plain: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            disable_web_page_preview=disable_preview,
            business_connection_id=update.business_message.business_connection_id
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for /start command"""
    if not update.message or not update.effective_chat or not update.effective_user:
        return
    
    # Логируем команду
    log_message(
        chat_id=update.effective_chat.id,
        user_id=update.effective_user.id,
        username=update.effective_user.username,
        message_type="COMMAND",
        content="/start",
        message_id=update.message.message_id
    )
    
    welcome_message = (
        "🤖 Привет! Я бот с интеграцией GPT-5 через NeuroAPI.\n\n"
        "Просто отправьте мне сообщение, и я отвечу с помощью искусственного интеллекта.\n"
        f"Контекст диалога: {'включен' if config.ENABLE_CONTEXT else 'отключен'}\n"
        f"Голосовые сообщения: {'поддерживаются' if config.ENABLE_VOICE else 'не поддерживаются'}\n\n"
        "Используйте /help для получения списка команд."
    )
    
    try:
        await _reply_md_v2_safe(update, context, welcome_message)
        log_response(update.effective_chat.id, "TEXT", True)
    except Exception as e:
        log_response(update.effective_chat.id, "TEXT", False, str(e))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for /help command"""
    if not update.message or not update.effective_chat or not update.effective_user:
        return
    
    # Логируем команду
    log_message(
        chat_id=update.effective_chat.id,
        user_id=update.effective_user.id,
        username=update.effective_user.username,
        message_type="COMMAND",
        content="/help",
        message_id=update.message.message_id
    )
    
    help_text = (
        "📋 *Доступные команды:*\n\n"
        "/start - Начать общение с ботом\n"
        "/help - Показать это сообщение\n"
        "/ping - Проверить работу бота\n\n"
        "💬 *Как использовать:*\n"
        "Просто отправьте текстовое сообщение, и я отвечу с помощью GPT-5.\n"
    )
    
    if config.ENABLE_VOICE:
        help_text += "\n🎤 *Голосовые сообщения:*\nОтправьте голосовое сообщение, и я распознаю речь и отвечу."
    
    if config.ENABLE_CONTEXT:
        help_text += "\n🧠 *Контекст:*\nЯ помню предыдущие сообщения в рамках нашего диалога."
    
    try:
        await _reply_md_v2_safe(update, context, help_text)
        log_response(update.effective_chat.id, "TEXT", True)
    except Exception as e:
        log_response(update.effective_chat.id, "TEXT", False, str(e))

async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for /ping command - bot health check"""
    if not update.message or not update.effective_chat or not update.effective_user:
        return
    
    # Логируем команду
    log_message(
        chat_id=update.effective_chat.id,
        user_id=update.effective_user.id,
        username=update.effective_user.username,
        message_type="COMMAND",
        content="/ping",
        message_id=update.message.message_id
    )
    
    ping_message = (
        "🏓 Pong!\n"
        f"Бот работает нормально.\n"
        f"Версия: 1.0.0\n"
        f"NeuroAPI GPT-5: {'✅ настроен' if config.NEUROAPI_API_KEY else '❌ не настроен'}\n"
        f"Голосовые функции: {'✅ включены' if config.ENABLE_VOICE else '❌ отключены'}"
    )
    
    try:
        await _reply_md_v2_safe(update, context, ping_message)
        log_response(update.effective_chat.id, "TEXT", True)
    except Exception as e:
        log_response(update.effective_chat.id, "TEXT", False, str(e))

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for text messages (both regular and business messages)"""
    # Проверяем, является ли это business_message
    if update.business_message:
        await handle_business_message(update, context)
        return
    
    # Обрабатываем обычное сообщение
    if not update.message or not update.effective_chat or not update.effective_user:
        return
    
    user_message = update.message.text or ""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    username = update.effective_user.username
    message_id = update.message.message_id

    # Логируем входящее текстовое сообщение
    log_message(
        chat_id=chat_id,
        user_id=user_id,
        username=username,
        message_type="TEXT",
        content=user_message,
        message_id=message_id
    )

    try:
        # Отправляем статус "печатает"
        logger.info(f"Processing text message from chat {chat_id}: {user_message[:50]}...")
        await _send_typing_status(update, context)
        
        # Get response from NeuroAPI GPT-5
        gpt_response = get_gpt_response(user_message, chat_id)
        await _reply_md_v2_safe(update, context, gpt_response)
        log_response(chat_id, "TEXT", True)
    except Exception as e:
        logger.error(f"Error handling text message for chat {chat_id}: {str(e)}")
        log_response(chat_id, "TEXT", False, str(e))
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text="Извините, произошла ошибка при обработке вашего сообщения. Попробуйте позже."
            )
        except Exception as reply_error:
            logger.error(f"Error sending error reply: {reply_error}")

async def handle_business_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for business messages"""
    logger.info("handle_business_message called")
    
    if not update.business_message:
        logger.warning("No business_message in update")
        return
        
    if not update.effective_chat:
        logger.warning("No effective_chat in update")
        return
        
    if not update.effective_user:
        logger.warning("No effective_user in update")
        return
    
    user_message = update.business_message.text or ""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    username = update.effective_user.username
    message_id = update.business_message.message_id
    business_connection_id = update.business_message.business_connection_id

    # Логируем входящее бизнес-сообщение
    log_message(
        chat_id=chat_id,
        user_id=user_id,
        username=username,
        message_type="BUSINESS_MESSAGE",
        content=user_message,
        message_id=message_id
    )

    try:
        # Отправляем статус "печатает"
        logger.info(f"Processing business message from chat {chat_id}: {user_message[:50]}...")
        await _send_business_typing_status(update, context)
        
        # Get response from NeuroAPI GPT-5 with business context and connection ID
        gpt_response = get_gpt_response(user_message, chat_id, is_business_message=True, business_connection_id=business_connection_id)
        
        # Отправляем ответ в бизнес-чат с поддержкой MarkdownV2
        await _reply_business_md_v2_safe(update, context, gpt_response)
        
        log_response(chat_id, "BUSINESS_MESSAGE", True)
    except Exception as e:
        logger.error(f"Error handling business message for chat {chat_id}: {str(e)}")
        log_response(chat_id, "BUSINESS_MESSAGE", False, str(e))
        
        try:
            await _reply_business_md_v2_safe(update, context, "Привет! Я ИИ-ассистент Сергея. Произошла ошибка, но Сергей прочитает ваше сообщение и ответит как только сможет.")
        except Exception as reply_error:
            logger.error(f"Error sending error reply for business message: {reply_error}")