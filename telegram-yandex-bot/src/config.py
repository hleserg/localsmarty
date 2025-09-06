import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram Configuration
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    
    # Yandex Cloud Configuration
    YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
    YANDEX_FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")
    YANDEX_MODEL = os.getenv("YANDEX_MODEL", "yandexgpt-lite/latest")
    YANDEX_ENDPOINT = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # API Settings
    DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))
    DEFAULT_MAX_TOKENS = int(os.getenv("DEFAULT_MAX_TOKENS", "1000"))
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))

config = Config()