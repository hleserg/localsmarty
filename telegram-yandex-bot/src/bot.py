import os
import logging
import json
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from handlers.commands import start, help_command, ping_command, handle_text_message, handle_business_message
from handlers.voice import handle_voice_message, handle_audio_message
from config import config
from dotenv import load_dotenv
from utils.logger import logger, log_info, log_error, log_update_json
from aiohttp import web

# Load environment variables
load_dotenv()

async def log_all_updates(update: Update, context):
    """Middleware для логирования всех входящих updates в виде JSON"""
    try:
        # Конвертируем update в словарь
        update_dict = update.to_dict()
        
        # Логируем полный JSON
        log_update_json(update_dict)
        
    except Exception as e:
        logger.error(f"Error logging update JSON: {e}")

async def webhook_handler(request):
    """Обработчик webhook запросов"""
    try:
        # Получаем данные из запроса
        data = await request.json()
        
        # Создаем Update объект
        update = Update.de_json(data, None)
        
        # Обрабатываем update через стандартную систему
        await application.process_update(update)
        
        return web.Response(text="OK")
        
    except Exception as e:
        log_error(f"Error processing webhook: {e}")
        return web.Response(text="Error", status=500)


async def health_handler(request):
    """Health check endpoint"""
    return web.Response(text="OK", status=200)

async def status_handler(request):
    """Status endpoint"""
    status = {
        "status": "running",
        "webhook_url": f"{config.WEBHOOK_URL}{config.WEBHOOK_PATH}",
        "port": config.WEBHOOK_PORT,
        "voice_enabled": config.ENABLE_VOICE,
        "context_enabled": config.ENABLE_CONTEXT
    }
    return web.json_response(status)

async def setup_webhook():
    """Настройка webhook"""
    try:
        # Удаляем старый webhook если есть
        await application.bot.delete_webhook()
        log_info("Old webhook deleted")
        
        # Устанавливаем новый webhook с allowed_updates
        webhook_url = f"{config.WEBHOOK_URL}{config.WEBHOOK_PATH}"
        allowed_updates = [
            "message",
            "edited_message", 
            "business_connection",
            "business_message",
            "edited_business_message",
            "deleted_business_messages"
        ]
        
        await application.bot.set_webhook(
            url=webhook_url,
            allowed_updates=allowed_updates,
            secret_token=config.WEBHOOK_SECRET_TOKEN
        )
        log_info(f"Webhook set to: {webhook_url}")
        log_info(f"Allowed updates: {allowed_updates}")
        
    except Exception as e:
        log_error(f"Error setting webhook: {e}")

async def init_app():
    """Инициализация приложения"""
    # Создаем aiohttp приложение
    app = web.Application()
    
    # Добавляем маршруты
    app.router.add_post(config.WEBHOOK_PATH, webhook_handler)
    app.router.add_get('/health', health_handler)
    app.router.add_get('/', status_handler)
    
    return app

def main() -> None:
    """Start the bot"""
    global application
    
    # Validate configuration
    if not config.TELEGRAM_TOKEN:
        log_error("TELEGRAM_TOKEN is not set")
        return
    
    if not config.NEUROAPI_API_KEY:
        log_error("NEUROAPI_API_KEY is not set")
        return
    
    log_info("Starting Telegram bot with NeuroAPI GPT-5 integration")
    log_info(f"Voice mode: {'enabled' if config.ENABLE_VOICE else 'disabled'}")
    log_info(f"Context mode: {'enabled' if config.ENABLE_CONTEXT else 'disabled'}")
    log_info("Message logging is enabled - all incoming messages will be logged")
    log_info("Full JSON update logging is enabled - all updates will be logged to updates.json")
    
    # Create application
    application = Application.builder().token(config.TELEGRAM_TOKEN).build()
    
    # Add middleware for logging all updates as JSON
    application.add_handler(MessageHandler(filters.ALL, log_all_updates), group=-1)
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ping", ping_command))
    
    # Add message handlers (обрабатывает как обычные, так и business сообщения)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    log_info("Message handler registered (supports both regular and business messages)")
    
    # Add voice handlers if enabled
    if config.ENABLE_VOICE:
        application.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
        application.add_handler(MessageHandler(filters.AUDIO, handle_audio_message))
        log_info("Voice message handlers registered")
    
    # Инициализируем приложение
    async def start_server():
        # Настраиваем webhook
        await setup_webhook()
        
        # Создаем aiohttp приложение
        app = await init_app()
        
        # Запускаем сервер
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, config.WEBHOOK_HOST, config.WEBHOOK_PORT)
        await site.start()
        
        log_info(f"Webhook server started on {config.WEBHOOK_HOST}:{config.WEBHOOK_PORT}")
        log_info(f"Webhook URL: {config.WEBHOOK_URL}{config.WEBHOOK_PATH}")
        
        # Ждем завершения
        try:
            await asyncio.Future()  # Бесконечное ожидание
        except KeyboardInterrupt:
            log_info("Shutting down...")
            await application.bot.delete_webhook()
            await runner.cleanup()
    
    # Запускаем сервер
    asyncio.run(start_server())

if __name__ == '__main__':
    main()