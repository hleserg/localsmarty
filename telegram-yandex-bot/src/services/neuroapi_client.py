import requests
import logging
from typing import List, Dict, Optional
from config import config

logger = logging.getLogger(__name__)

class NeuroAPIClient:
    def __init__(self):
        self.api_key = config.NEUROAPI_API_KEY
        self.endpoint = "https://neuroapi.host/v1/chat/completions"
        self.model = "gpt-5"
        
        # HTTP session with retries
        self.session = requests.Session()
        try:
            from requests.adapters import HTTPAdapter
            from urllib3.util import Retry
            retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
            self.session.mount("https://", HTTPAdapter(max_retries=retries))
        except Exception:
            # Fallback: no retries if urllib3 not available
            pass

        # Chat context storage (in-memory for MVP)
        self.chat_contexts: Dict[int, List[Dict[str, str]]] = {}
        
    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests"""
        if not self.api_key:
            raise ValueError("NEUROAPI_API_KEY is not set")
            
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        return headers
    
    def _prepare_messages(self, user_message: str, chat_id: int, is_business_message: bool = False) -> List[Dict[str, str]]:
        """Prepare messages for the API request with context"""
        
        # Выбираем системный промпт в зависимости от типа сообщения
        if is_business_message:
            system_content = (
                "Ты — ИИ-ассистент Сергея Хлебникова. Ты помогаешь клиентам в его бизнес-чате. "
                "Твоя роль:\n"
                "• Представляйся как ИИ-ассистент Сергея\n"
                "• Объясняй, что Сергей прочитает их сообщение и ответит как только сможет\n"
                "• Предлагай свою помощь, если можешь быть полезен\n"
                "• Будь вежливым, профессиональным и дружелюбным\n"
                "• Отвечай на русском языке\n"
                "• Если не можешь помочь с вопросом, предложи клиенту дождаться ответа Сергея"
            )
        else:
            system_content = "Ты — полезный Telegram-бот. Отвечай дружелюбно и информативно на русском языке."
        
        messages = [
            {"role": "system", "content": system_content}
        ]
        
        if config.ENABLE_CONTEXT and chat_id in self.chat_contexts:
            # Add recent context (last 10 messages to stay within limits)
            context = self.chat_contexts[chat_id][-10:]
            messages.extend(context)
            
        messages.append({"role": "user", "content": user_message})
        return messages
    
    def _update_context(self, chat_id: int, user_message: str, assistant_response: str):
        """Update chat context with new messages"""
        if not config.ENABLE_CONTEXT:
            return
            
        if chat_id not in self.chat_contexts:
            self.chat_contexts[chat_id] = []
            
        context = self.chat_contexts[chat_id]
        context.extend([
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": assistant_response}
        ])
        
        # Keep only last 20 messages (10 pairs) to manage memory
        if len(context) > 20:
            self.chat_contexts[chat_id] = context[-20:]
    
    def get_response(self, user_message: str, chat_id: int, is_business_message: bool = False) -> str:
        """Get response from NeuroAPI GPT-5"""
        if not user_message.strip():
            return "Ошибка: пустой ввод"
            
        # Limit message length
        if len(user_message) > 4000:
            user_message = user_message[:4000]
            logger.warning(f"Message truncated to 4000 characters for chat {chat_id}")
        
        try:
            headers = self._get_headers()
            messages = self._prepare_messages(user_message, chat_id, is_business_message)
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": config.NEUROAPI_TEMPERATURE,
                "max_tokens": config.NEUROAPI_MAX_TOKENS,
                "stream": False
            }
            
            message_type = "business" if is_business_message else "regular"
            logger.info(f"Sending request to NeuroAPI GPT-5 for chat {chat_id} ({message_type} message)")
            response = requests.post(
                self.endpoint, 
                headers=headers, 
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.debug(f"NeuroAPI response for chat {chat_id}: {result}")
                assistant_message = result["choices"][0]["message"]["content"]
                
                # Проверяем, что ответ не пустой
                if not assistant_message or not assistant_message.strip():
                    logger.warning(f"Empty response from NeuroAPI for chat {chat_id}")
                    if is_business_message:
                        assistant_message = "Привет! Я ИИ-ассистент Сергея. Он прочитает ваше сообщение и ответит как только сможет. Чем могу помочь?"
                    else:
                        assistant_message = "Извините, я не смог сгенерировать ответ. Попробуйте еще раз."
                
                # Update context
                self._update_context(chat_id, user_message, assistant_message)
                
                logger.info(f"Successfully got response from NeuroAPI GPT-5 for chat {chat_id} ({message_type}): {assistant_message[:100]}...")
                return assistant_message
            else:
                error_msg = f"NeuroAPI Error {response.status_code}: {response.text}"
                logger.error(error_msg)
                if is_business_message:
                    return "Привет! Я ИИ-ассистент Сергея. Произошла техническая ошибка, но Сергей прочитает ваше сообщение и ответит как только сможет."
                else:
                    return f"Извините, произошла ошибка при обращении к GPT-5. Попробуйте позже."
                
        except requests.exceptions.Timeout:
            logger.error(f"Timeout error for chat {chat_id}")
            if is_business_message:
                return "Привет! Я ИИ-ассистент Сергея. Произошла задержка, но Сергей прочитает ваше сообщение и ответит как только сможет."
            else:
                return "Превышено время ожидания ответа. Попробуйте еще раз."
        except Exception as e:
            logger.error(f"Unexpected error for chat {chat_id}: {str(e)}")
            if is_business_message:
                return "Привет! Я ИИ-ассистент Сергея. Произошла техническая ошибка, но Сергей прочитает ваше сообщение и ответит как только сможет."
            else:
                return "Произошла техническая ошибка. Попробуйте позже."

# Global client instance
neuroapi_client = NeuroAPIClient()

def get_gpt_response(user_message: str, chat_id: int = 0, is_business_message: bool = False) -> str:
    """Backward compatibility function"""
    return neuroapi_client.get_response(user_message, chat_id, is_business_message)
