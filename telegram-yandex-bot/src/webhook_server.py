import os
import logging
import asyncio
import ssl
from aiohttp import web, web_request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from handlers.commands import start, help_command, ping_command, handle_text_message
from handlers.voice import handle_voice_message, handle_audio_message
from config import config
from dotenv import load_dotenv
from utils.logger import logger, log_info, log_error, log_update_json

# Load environment variables
load_dotenv()

# Global application instance
application = None

async def log_all_updates(update: Update, context):
    """Middleware для логирования всех входящих updates в виде JSON"""
    try:
        # Конвертируем update в словарь
        update_dict = update.to_dict()
        
        # Логируем полный JSON
        log_update_json(update_dict)
        
    except Exception as e:
        logger.error(f"Error logging update JSON: {e}")

async def webhook_handler(request: web_request.Request) -> web.Response:
    """Обработчик webhook запросов от Telegram"""
    try:
        # Получаем данные из запроса
        data = await request.json()
        
        # Логируем входящий webhook
        log_info(f"📥 Webhook received: {len(str(data))} bytes")
        
        # Создаем Update объект
        update = Update.de_json(data, application.bot)
        
        # Обрабатываем update
        await application.process_update(update)
        
        return web.Response(text="OK", status=200)
        
    except Exception as e:
        log_error(f"Error processing webhook: {e}")
        return web.Response(text="Error", status=500)

async def health_check(request: web_request.Request) -> web.Response:
    """Проверка здоровья сервера"""
    return web.Response(text="Bot is running", status=200)

async def setup_application():
    """Настройка Telegram приложения"""
    global application
    
    # Validate configuration
    if not config.TELEGRAM_TOKEN:
        log_error("TELEGRAM_TOKEN is not set")
        return None
    
    if not config.NEUROAPI_API_KEY:
        log_error("NEUROAPI_API_KEY is not set")
        return None
    
    log_info("🚀 Starting Telegram bot with NeuroAPI GPT-5 integration (Webhook mode)")
    log_info(f"🎤 Voice mode: {'enabled' if config.ENABLE_VOICE else 'disabled'}")
    log_info(f"🧠 Context mode: {'enabled' if config.ENABLE_CONTEXT else 'disabled'}")
    log_info("📝 Message logging is enabled - all incoming messages will be logged")
    log_info("📄 Full JSON update logging is enabled - all updates will be logged to updates.json")
    
    # Create application
    application = Application.builder().token(config.TELEGRAM_TOKEN).build()
    
    # Add middleware for logging all updates as JSON
    application.add_handler(MessageHandler(filters.ALL, log_all_updates), group=-1)
    
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
        log_info("🎤 Voice message handlers registered")
    
    # Initialize application
    await application.initialize()
    
    return application

async def setup_webhook():
    """Настройка webhook"""
    if not config.WEBHOOK_URL:
        log_error("WEBHOOK_URL is not set")
        return False
    
    webhook_url = f"{config.WEBHOOK_URL}{config.WEBHOOK_PATH}"
    
    # Удаляем старый webhook
    await application.bot.delete_webhook()
    log_info("🗑️ Old webhook deleted")
    
    # Устанавливаем новый webhook
    await application.bot.set_webhook(
        url=webhook_url,
        secret_token=config.WEBHOOK_SECRET_TOKEN
    )
    
    log_info(f"🔗 Webhook set to: {webhook_url}")
    return True

async def create_app():
    """Создание web приложения"""
    app = web.Application()
    
    # Настраиваем маршруты
    app.router.add_post(config.WEBHOOK_PATH, webhook_handler)
    app.router.add_get("/health", health_check)
    app.router.add_get("/", health_check)
    
    return app

async def start_webhook_server():
    """Запуск webhook сервера"""
    # Настраиваем приложение
    app_instance = await setup_application()
    if not app_instance:
        return
    
    # Создаем web приложение
    app = await create_app()
    
    # Настраиваем webhook
    webhook_setup_success = await setup_webhook()
    if not webhook_setup_success:
        return
    
    # Настраиваем SSL если указаны сертификаты
    ssl_context = None
    if config.SSL_CERT_PATH and config.SSL_KEY_PATH:
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(config.SSL_CERT_PATH, config.SSL_KEY_PATH)
        log_info(f"🔒 SSL enabled with cert: {config.SSL_CERT_PATH}")
    else:
        log_info("⚠️ SSL disabled - using HTTP (not recommended for production)")
    
    # Запускаем сервер
    log_info(f"🌐 Starting webhook server on {config.WEBHOOK_HOST}:{config.WEBHOOK_PORT}")
    log_info(f"📡 Webhook path: {config.WEBHOOK_PATH}")
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(
        runner, 
        config.WEBHOOK_HOST, 
        config.WEBHOOK_PORT,
        ssl_context=ssl_context
    )
    
    await site.start()
    
    log_info("✅ Webhook server started successfully!")
    log_info("🤖 Bot is ready to receive updates via webhook")
    
    # Держим сервер запущенным
    try:
        await asyncio.Future()  # Запускаем бесконечный цикл
    except KeyboardInterrupt:
        log_info("🛑 Shutting down webhook server...")
        await application.shutdown()
        await runner.cleanup()

def main():
    """Главная функция"""
    try:
        asyncio.run(start_webhook_server())
    except KeyboardInterrupt:
        log_info("🛑 Bot stopped by user")
    except Exception as e:
        log_error(f"❌ Error starting webhook server: {e}")

if __name__ == '__main__':
    main()
