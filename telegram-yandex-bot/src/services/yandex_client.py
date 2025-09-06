import requests
import os
import logging
from config import config

logger = logging.getLogger(__name__)

class YandexClient:
    def __init__(self):
        self.api_key = os.getenv('YANDEX_API_KEY')
        self.folder_id = os.getenv('YANDEX_FOLDER_ID')
        self.model = os.getenv('YANDEX_MODEL', 'yandexgpt-lite/latest')
        self.api_url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'
        
        if not self.api_key:
            raise ValueError("YANDEX_API_KEY environment variable is required")
        if not self.folder_id:
            raise ValueError("YANDEX_FOLDER_ID environment variable is required")

    def get_response(self, prompt, temperature=0.7, max_tokens=1000):
        """
        Получить ответ от Yandex GPT
        
        Args:
            prompt (str): Текст запроса пользователя
            temperature (float): Температура для генерации (0.0-1.0)
            max_tokens (int): Максимальное количество токенов в ответе
            
        Returns:
            str: Ответ от YandexGPT
        """
        headers = {
            'Authorization': f'Api-Key {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'modelUri': f'gpt://{self.folder_id}/{self.model}',
            'completionOptions': {
                'stream': False,
                'temperature': temperature,
                'maxTokens': max_tokens
            },
            'messages': [
                {
                    'role': 'user',
                    'text': prompt
                }
            ]
        }
        
        try:
            logger.info(f"Sending request to YandexGPT with prompt length: {len(prompt)}")
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'result' in result and 'alternatives' in result['result']:
                    alternatives = result['result']['alternatives']
                    if alternatives and len(alternatives) > 0:
                        message_text = alternatives[0]['message']['text']
                        logger.info(f"Received response from YandexGPT with length: {len(message_text)}")
                        return message_text
                    else:
                        logger.error("No alternatives in YandexGPT response")
                        return "Извините, не удалось получить ответ от AI."
                else:
                    logger.error(f"Unexpected response format: {result}")
                    return "Извините, получен некорректный ответ от AI."
            else:
                logger.error(f"YandexGPT API error: {response.status_code}, {response.text}")
                return f"Ошибка при обращении к AI: {response.status_code}"
                
        except requests.exceptions.Timeout:
            logger.error("Timeout when calling YandexGPT API")
            return "Извините, превышено время ожидания ответа от AI."
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception when calling YandexGPT API: {e}")
            return "Извините, произошла ошибка при обращении к AI."
        except Exception as e:
            logger.error(f"Unexpected error when calling YandexGPT API: {e}")
            return "Извините, произошла неожиданная ошибка."

# Создаем глобальный экземпляр клиента только если переменные окружения доступны
yandex_client = None

def _get_client():
    """Получить экземпляр клиента, создать если не существует"""
    global yandex_client
    if yandex_client is None:
        yandex_client = YandexClient()
    return yandex_client

def get_gpt_response(prompt, temperature=0.7, max_tokens=1000):
    """
    Функция-обертка для получения ответа от YandexGPT
    
    Args:
        prompt (str): Текст запроса пользователя
        temperature (float): Температура для генерации
        max_tokens (int): Максимальное количество токенов
        
    Returns:
        str: Ответ от YandexGPT
    """
    try:
        client = _get_client()
        return client.get_response(prompt, temperature, max_tokens)
    except ValueError as e:
        # Если нет переменных окружения, возвращаем ошибку
        return f"Ошибка конфигурации: {str(e)}"