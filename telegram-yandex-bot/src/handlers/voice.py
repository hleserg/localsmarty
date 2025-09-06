import logging
import io
from telegram import Update
from io import BytesIO
from telegram.ext import ContextTypes
from services.yandex_client import get_gpt_response
from handlers.commands import _reply_md_v2_safe
from services.speech_client import speech_client
from config import config

logger = logging.getLogger(__name__)

async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for voice messages"""
    if not config.ENABLE_VOICE:
        if update.message:
            await _reply_md_v2_safe(update, "Голосовые сообщения отключены. Пожалуйста, отправьте текстовое сообщение.")
        return

    if not update.message or not update.effective_chat or not update.message.voice:
        return

    chat_id = update.effective_chat.id
    voice = update.message.voice

    logger.info(f"Received voice message from chat {chat_id}, duration: {voice.duration}s")

    # Check duration limit
    if voice.duration > config.AUDIO_MAX_DURATION_SEC:
        await _reply_md_v2_safe(update, f"Голосовое сообщение слишком длинное (макс. {config.AUDIO_MAX_DURATION_SEC} сек). Пожалуйста, отправьте более короткое сообщение.")
        return

    try:
        # Download voice file
        voice_file = await context.bot.get_file(voice.file_id)
        voice_bytes = io.BytesIO()
        await voice_file.download_to_memory(out=voice_bytes)
        audio_data = voice_bytes.getvalue()

        logger.info(f"Downloaded voice file, size: {len(audio_data)} bytes")

        # Convert speech to text
        await _reply_md_v2_safe(update, "🎤 Обрабатываю голосовое сообщение...")

        recognized_text = speech_client.speech_to_text(audio_data)
        if not recognized_text:
            await _reply_md_v2_safe(update, "Не удалось распознать речь. Попробуйте еще раз или отправьте текстовое сообщение.")
            return

        logger.info(f"Recognized text: {recognized_text[:100]}...")

        # Show recognized text to user
        await _reply_md_v2_safe(update, f"🗣️ Распознано: {recognized_text}")

        # Get GPT response
        gpt_response = get_gpt_response(recognized_text, chat_id)

        # Send text response
        await _reply_md_v2_safe(update, f"🤖 {gpt_response}")

        # Optionally send voice response (TTS)
        if config.ENABLE_TTS_REPLY:
            tts_audio = speech_client.text_to_speech(gpt_response)
            if tts_audio:
                await update.message.reply_voice(voice=BytesIO(tts_audio))
            else:
                logger.warning("TTS generation failed; sending text only")

        logger.info(f"Successfully processed voice message for chat {chat_id}")

    except Exception as e:
        logger.error(f"Error processing voice message for chat {chat_id}: {str(e)}")
        if update.message:
            await _reply_md_v2_safe(update, "Произошла ошибка при обработке голосового сообщения. Попробуйте еще раз или отправьте текст.")

async def handle_audio_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for audio messages (similar to voice but for audio files)"""
    if not config.ENABLE_VOICE:
        if update.message:
            await _reply_md_v2_safe(update, "Аудиосообщения отключены. Пожалуйста, отправьте текстовое сообщение.")
        return
    
    # For simplicity, redirect audio to voice handler
    # In a more sophisticated implementation, we might handle different audio formats
    await handle_voice_message(update, context)