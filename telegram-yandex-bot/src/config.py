import os
from typing import Optional

class Config:
    # Telegram Configuration
    TELEGRAM_TOKEN: Optional[str] = os.getenv("TELEGRAM_TOKEN")
    
    # NeuroAPI Configuration
    NEUROAPI_API_KEY: Optional[str] = os.getenv("NEUROAPI_API_KEY")
    NEUROAPI_TEMPERATURE: float = float(os.getenv("NEUROAPI_TEMPERATURE", "0.7"))
    NEUROAPI_MAX_TOKENS: int = int(os.getenv("NEUROAPI_MAX_TOKENS", "1000"))
    
    # Yandex Cloud Configuration (legacy, kept for compatibility)
    YC_FOLDER_ID: Optional[str] = os.getenv("YC_FOLDER_ID")
    YC_API_KEY: Optional[str] = os.getenv("YC_API_KEY")  # optional; prefer IAM via SA key
    YC_IAM_TOKEN: Optional[str] = os.getenv("YC_IAM_TOKEN")  # optional fallback/manual
    # Service Account key for automatic IAM token retrieval
    YC_SA_KEY_FILE: Optional[str] = os.getenv("YC_SA_KEY_FILE")
    YC_SA_KEY_JSON: Optional[str] = os.getenv("YC_SA_KEY_JSON")
    
    # Model Configuration (legacy)
    YC_MODEL_URI: Optional[str] = os.getenv("YC_MODEL_URI")
    YC_TEMPERATURE: float = float(os.getenv("YC_TEMPERATURE", "0.3"))
    YC_MAX_TOKENS: int = int(os.getenv("YC_MAX_TOKENS", "800"))
    
    # Bot Configuration
    ENABLE_CONTEXT: bool = os.getenv("ENABLE_CONTEXT", "true").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Webhook Configuration
    WEBHOOK_URL: Optional[str] = os.getenv("WEBHOOK_URL", "https://talkbot.skhlebnikov.ru")
    WEBHOOK_PORT: int = int(os.getenv("WEBHOOK_PORT", "11844"))
    WEBHOOK_HOST: str = os.getenv("WEBHOOK_HOST", "0.0.0.0")
    WEBHOOK_PATH: str = os.getenv("WEBHOOK_PATH", "/bot")
    # SSL сертификаты не нужны - обрабатываются Hestia
    SSL_CERT_PATH: Optional[str] = None
    SSL_KEY_PATH: Optional[str] = None
    WEBHOOK_SECRET_TOKEN: Optional[str] = os.getenv("WEBHOOK_SECRET_TOKEN")
    
    # Voice Configuration
    ENABLE_VOICE: bool = os.getenv("ENABLE_VOICE", "false").lower() == "true"
    STT_LANGUAGE: str = os.getenv("STT_LANGUAGE", "ru-RU")
    TTS_VOICE: str = os.getenv("TTS_VOICE", "alena")
    TTS_FORMAT: str = os.getenv("TTS_FORMAT", "oggopus")
    AUDIO_MAX_DURATION_SEC: int = int(os.getenv("AUDIO_MAX_DURATION_SEC", "60"))
    ENABLE_TTS_REPLY: bool = os.getenv("ENABLE_TTS_REPLY", "false").lower() == "true"
    
    # API Endpoints
    YC_FOUNDATION_MODELS_ENDPOINT = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    YC_STT_ENDPOINT = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"
    YC_TTS_ENDPOINT = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
    YC_IAM_ENDPOINT = "https://iam.api.cloud.yandex.net/iam/v1/tokens"

config = Config()