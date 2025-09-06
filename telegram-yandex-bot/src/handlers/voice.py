import logging
import io
from telegram import Update
from telegram.ext import CallbackContext
from services.yandex_client import get_gpt_response
from services.speech_client import speech_client
from config import config

logger = logging.getLogger(__name__)

def handle_voice_message(update: Update, context: CallbackContext) -> None:
    """Handler for voice messages"""
    if not config.ENABLE_VOICE:
        update.message.reply_text(
            "Голосовые сообщения отключены. Пожалуйста, отправьте текстовое сообщение."
        )
        return
    
    chat_id = update.effective_chat.id
    voice = update.message.voice
    
    logger.info(f"Received voice message from chat {chat_id}, duration: {voice.duration}s")
    
    # Check duration limit
    if voice.duration > config.AUDIO_MAX_DURATION_SEC:
        update.message.reply_text(
            f"Голосовое сообщение слишком длинное (макс. {config.AUDIO_MAX_DURATION_SEC} сек). "
            "Пожалуйста, отправьте более короткое сообщение."
        )
        return
    
    try:
        # Download voice file
        voice_file = context.bot.get_file(voice.file_id)
        voice_bytes = io.BytesIO()
        voice_file.download(out=voice_bytes)
        audio_data = voice_bytes.getvalue()
        
        logger.info(f"Downloaded voice file, size: {len(audio_data)} bytes")
        
        # Convert speech to text
        update.message.reply_text("🎤 Обрабатываю голосовое сообщение...")
        
        recognized_text = speech_client.speech_to_text(audio_data)
        
        if not recognized_text:
            update.message.reply_text(
                "Не удалось распознать речь. Попробуйте еще раз или отправьте текстовое сообщение."
            )
            return
        
        logger.info(f"Recognized text: {recognized_text[:100]}...")
        
        # Show recognized text to user
        update.message.reply_text(f"🗣️ Распознано: {recognized_text}")
        
        # Get GPT response
        gpt_response = get_gpt_response(recognized_text, chat_id)
        
        # Send text response
        update.message.reply_text(f"🤖 {gpt_response}")
        
        # Optionally send voice response (TTS)
        # For MVP, we'll skip this to keep it simple
        # In future versions, this could be configurable
        
        logger.info(f"Successfully processed voice message for chat {chat_id}")
        
    except Exception as e:
        logger.error(f"Error processing voice message for chat {chat_id}: {str(e)}")
        update.message.reply_text(
            "Произошла ошибка при обработке голосового сообщения. Попробуйте еще раз или отправьте текст."
        )

def handle_audio_message(update: Update, context: CallbackContext) -> None:
    """Handler for audio messages (similar to voice but for audio files)"""
    if not config.ENABLE_VOICE:
        update.message.reply_text(
            "Аудиосообщения отключены. Пожалуйста, отправьте текстовое сообщение."
        )
        return
    
    # For simplicity, redirect audio to voice handler
    # In a more sophisticated implementation, we might handle different audio formats
    handle_voice_message(update, context)