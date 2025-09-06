import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from handlers.commands import start, help_command, ping_command, handle_text_message
from handlers.voice import handle_voice_message, handle_audio_message
from config import config
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
)
logger = logging.getLogger(__name__)

def main() -> None:
    """Start the bot"""
    # Validate configuration
    if not config.TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN is not set")
        return
    
    if not config.YC_FOLDER_ID:
        logger.error("YC_FOLDER_ID is not set")
        return
    
    if not (config.YC_SA_KEY_FILE or config.YC_SA_KEY_JSON or config.YC_IAM_TOKEN or config.YC_API_KEY):
        logger.error("Credentials missing: set YC_SA_KEY_FILE or YC_SA_KEY_JSON (preferred), or YC_IAM_TOKEN / YC_API_KEY")
        return
    
    logger.info("Starting Telegram bot with YandexGPT integration")
    logger.info(f"Voice mode: {'enabled' if config.ENABLE_VOICE else 'disabled'}")
    logger.info(f"Context mode: {'enabled' if config.ENABLE_CONTEXT else 'disabled'}")
    
    # Create application
    application = Application.builder().token(config.TELEGRAM_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ping", ping_command))
    
    # Add message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    # Add voice handlers if enabled
    if config.ENABLE_VOICE:
        application.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
        application.add_handler(MessageHandler(filters.AUDIO, handle_audio_message))
        logger.info("Voice message handlers registered")
    
    # Start the bot
    logger.info("Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()