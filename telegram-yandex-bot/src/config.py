import os

class Config:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
    YANDEX_MODEL = "gpt-3.5-turbo"  # Укажите нужную модель Яндекс GPT
    YANDEX_ENDPOINT = "https://api.yandex.cloud/ai/gpt/v1/chat/completions"  # Укажите нужный эндпоинт
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")  # Уровень логирования, по умолчанию INFO

config = Config()