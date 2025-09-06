import os
from typing import Optional

class Config:
    # Telegram Configuration
    TELEGRAM_TOKEN: Optional[str] = os.getenv("TELEGRAM_TOKEN")
    
    # Yandex Cloud Configuration
    YC_FOLDER_ID: Optional[str] = os.getenv("YC_FOLDER_ID")
    YC_API_KEY: Optional[str] = os.getenv("YC_API_KEY")
    YC_IAM_TOKEN: Optional[str] = os.getenv("YC_IAM_TOKEN")
    
    # Model Configuration
    YC_MODEL_URI: Optional[str] = os.getenv("YC_MODEL_URI")
    YC_TEMPERATURE: float = float(os.getenv("YC_TEMPERATURE", "0.3"))
    YC_MAX_TOKENS: int = int(os.getenv("YC_MAX_TOKENS", "800"))
    
    # Bot Configuration
    ENABLE_CONTEXT: bool = os.getenv("ENABLE_CONTEXT", "true").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Voice Configuration
    ENABLE_VOICE: bool = os.getenv("ENABLE_VOICE", "false").lower() == "true"
    STT_LANGUAGE: str = os.getenv("STT_LANGUAGE", "ru-RU")
    TTS_VOICE: str = os.getenv("TTS_VOICE", "alena")
    TTS_FORMAT: str = os.getenv("TTS_FORMAT", "oggopus")
    AUDIO_MAX_DURATION_SEC: int = int(os.getenv("AUDIO_MAX_DURATION_SEC", "60"))
    
    # API Endpoints
    YC_FOUNDATION_MODELS_ENDPOINT = "https://llm.api.cloud.yandex.net/foundationModels/v1/chat/completion"
    YC_STT_ENDPOINT = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"
    YC_TTS_ENDPOINT = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"

config = Config()