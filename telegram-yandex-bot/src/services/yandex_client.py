import requests
import logging
from typing import List, Dict, Optional
from config import config

logger = logging.getLogger(__name__)

class YandexClient:
    def __init__(self):
        self.api_key = config.YC_API_KEY
        self.iam_token = config.YC_IAM_TOKEN
        self.folder_id = config.YC_FOLDER_ID
        self.model_uri = config.YC_MODEL_URI or f"gpt://{self.folder_id}/yandexgpt/latest"
        self.endpoint = config.YC_FOUNDATION_MODELS_ENDPOINT
        
        # Chat context storage (in-memory for MVP)
        self.chat_contexts: Dict[int, List[Dict[str, str]]] = {}
        
    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests"""
        headers = {
            "Content-Type": "application/json",
            "x-folder-id": self.folder_id
        }
        
        if self.api_key:
            headers["Authorization"] = f"Api-Key {self.api_key}"
        elif self.iam_token:
            headers["Authorization"] = f"Bearer {self.iam_token}"
        else:
            raise ValueError("Either YC_API_KEY or YC_IAM_TOKEN must be provided")
            
        return headers
    
    def _prepare_messages(self, user_message: str, chat_id: int) -> List[Dict[str, str]]:
        """Prepare messages for the API request with context"""
        messages = [
            {"role": "system", "text": "Ты — полезный Telegram-бот. Отвечай дружелюбно и информативно."}
        ]
        
        if config.ENABLE_CONTEXT and chat_id in self.chat_contexts:
            # Add recent context (last 10 messages to stay within limits)
            context = self.chat_contexts[chat_id][-10:]
            messages.extend(context)
            
        messages.append({"role": "user", "text": user_message})
        return messages
    
    def _update_context(self, chat_id: int, user_message: str, assistant_response: str):
        """Update chat context with new messages"""
        if not config.ENABLE_CONTEXT:
            return
            
        if chat_id not in self.chat_contexts:
            self.chat_contexts[chat_id] = []
            
        context = self.chat_contexts[chat_id]
        context.extend([
            {"role": "user", "text": user_message},
            {"role": "assistant", "text": assistant_response}
        ])
        
        # Keep only last 20 messages (10 pairs) to manage memory
        if len(context) > 20:
            self.chat_contexts[chat_id] = context[-20:]
    
    def get_response(self, user_message: str, chat_id: int) -> str:
        """Get response from Yandex GPT using Foundation Models API"""
        if not user_message.strip():
            return "Ошибка: пустой ввод"
            
        # Limit message length
        if len(user_message) > 4000:
            user_message = user_message[:4000]
            logger.warning(f"Message truncated to 4000 characters for chat {chat_id}")
        
        try:
            headers = self._get_headers()
            messages = self._prepare_messages(user_message, chat_id)
            
            payload = {
                "modelUri": self.model_uri,
                "completionOptions": {
                    "stream": False,
                    "temperature": config.YC_TEMPERATURE,
                    "maxTokens": config.YC_MAX_TOKENS
                },
                "messages": messages
            }
            
            logger.info(f"Sending request to Yandex GPT for chat {chat_id}")
            response = requests.post(
                self.endpoint, 
                headers=headers, 
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                assistant_message = result["result"]["alternatives"][0]["message"]["text"]
                
                # Update context
                self._update_context(chat_id, user_message, assistant_message)
                
                logger.info(f"Successfully got response for chat {chat_id}")
                return assistant_message
            else:
                error_msg = f"API Error {response.status_code}: {response.text}"
                logger.error(error_msg)
                return f"Извините, произошла ошибка при обращении к GPT. Попробуйте позже."
                
        except requests.exceptions.Timeout:
            logger.error(f"Timeout error for chat {chat_id}")
            return "Превышено время ожидания ответа. Попробуйте еще раз."
        except Exception as e:
            logger.error(f"Unexpected error for chat {chat_id}: {str(e)}")
            return "Произошла техническая ошибка. Попробуйте позже."

# Global client instance
yandex_client = YandexClient()

def get_gpt_response(user_message: str, chat_id: int = 0) -> str:
    """Backward compatibility function"""
    return yandex_client.get_response(user_message, chat_id)