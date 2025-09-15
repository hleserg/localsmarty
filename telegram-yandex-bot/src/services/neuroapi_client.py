import requests
import logging
import json
import os
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

        # Chat context storage (in-memory + file persistence)
        self.chat_contexts: Dict[str, List[Dict[str, str]]] = {}
        
        # Ensure logs directory exists
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        self.context_file = os.path.join(log_dir, "chat_contexts.json")
        self._load_contexts()
    
    def _load_contexts(self):
        """Load contexts from file"""
        try:
            if os.path.exists(self.context_file):
                with open(self.context_file, 'r', encoding='utf-8') as f:
                    self.chat_contexts = json.load(f)
                logger.info(f"Loaded {len(self.chat_contexts)} contexts from file")
            else:
                logger.info("No context file found, starting with empty contexts")
        except Exception as e:
            logger.error(f"Error loading contexts: {e}")
            self.chat_contexts = {}
    
    def _save_contexts(self):
        """Save contexts to file"""
        try:
            with open(self.context_file, 'w', encoding='utf-8') as f:
                json.dump(self.chat_contexts, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(self.chat_contexts)} contexts to file")
        except Exception as e:
            logger.error(f"Error saving contexts: {e}")
        
    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests"""
        if not self.api_key:
            raise ValueError("NEUROAPI_API_KEY is not set")
            
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        return headers
    
    def _prepare_messages(self, user_message: str, chat_id: int, is_business_message: bool = False, business_connection_id: str = None) -> List[Dict[str, str]]:
        """Prepare messages for the API request with context"""
        
        # Создаем уникальный ключ для контекста
        context_key = f"business_{business_connection_id}_{chat_id}" if is_business_message else chat_id
        
        # Отладочные логи
        logger.info(f"Context key: {context_key}")
        logger.info(f"Context exists: {context_key in self.chat_contexts}")
        if context_key in self.chat_contexts:
            logger.info(f"Context length: {len(self.chat_contexts[context_key])}")
            logger.info(f"Context content: {self.chat_contexts[context_key]}")
        
        # Выбираем системный промпт в зависимости от типа сообщения
        if is_business_message:
            # Для business сообщений используем более краткий системный промпт после первого сообщения
            if config.ENABLE_CONTEXT and context_key in self.chat_contexts and len(self.chat_contexts[context_key]) > 0:
                system_content = (
                    "Ты — ИИ-ассистент Сергея Хлебникова. Продолжай общение в том же стиле. "
                    "Сергей прочитает все сообщения и ответит как только сможет. "
                    "Будь полезным и дружелюбным."
                )
                logger.info("Using SHORT system prompt (context exists)")
            else:
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
                logger.info("Using FULL system prompt (no context)")
        else:
            system_content = "Ты — полезный Telegram-бот. Отвечай дружелюбно и информативно на русском языке."
        
        messages = [
            {"role": "system", "content": system_content}
        ]
        
        if config.ENABLE_CONTEXT and context_key in self.chat_contexts:
            # Add recent context (last 6 messages to stay within limits)
            context = self.chat_contexts[context_key][-6:]
            messages.extend(context)
            logger.info(f"Added {len(context)} context messages")
            
        messages.append({"role": "user", "content": user_message})
        logger.info(f"Total messages: {len(messages)}")
        return messages
    
    def _update_context(self, chat_id: int, user_message: str, assistant_response: str, is_business_message: bool = False, business_connection_id: str = None):
        """Update chat context with new messages"""
        if not config.ENABLE_CONTEXT:
            logger.info("Context disabled, skipping update")
            return
        
        # Создаем уникальный ключ для контекста
        context_key = f"business_{business_connection_id}_{chat_id}" if is_business_message else chat_id
        
        logger.info(f"Updating context for key: {context_key}")
        logger.info(f"User message: {user_message[:50]}...")
        logger.info(f"Assistant response: {assistant_response[:50]}...")
            
        if context_key not in self.chat_contexts:
            self.chat_contexts[context_key] = []
            logger.info(f"Created new context for key: {context_key}")
            
        context = self.chat_contexts[context_key]
        context.extend([
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": assistant_response}
        ])
        
        logger.info(f"Context updated. New length: {len(context)}")
        
        # Keep only last 20 messages (10 pairs) to manage memory
        if len(context) > 20:
            self.chat_contexts[context_key] = context[-20:]
            logger.info(f"Context trimmed to 20 messages")
        
        # Save contexts to file
        self._save_contexts()
    
    def get_response(self, user_message: str, chat_id: int, is_business_message: bool = False, business_connection_id: str = None) -> str:
        """Get response from NeuroAPI GPT-5"""
        if not user_message.strip():
            return "Ошибка: пустой ввод"
            
        # Limit message length
        if len(user_message) > 4000:
            user_message = user_message[:4000]
            logger.warning(f"Message truncated to 4000 characters for chat {chat_id}")
        
        try:
            headers = self._get_headers()
            messages = self._prepare_messages(user_message, chat_id, is_business_message, business_connection_id)
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": config.NEUROAPI_TEMPERATURE,
                "max_tokens": config.NEUROAPI_MAX_TOKENS,
                "stream": False
            }
            
            message_type = "business" if is_business_message else "regular"
            logger.info(f"Sending request to NeuroAPI GPT-5 for chat {chat_id} ({message_type} message)")
            
            # Retry логика для пустых ответов
            max_retries = 2
            assistant_message = None
            
            for attempt in range(max_retries + 1):
                response = requests.post(
                    self.endpoint, 
                    headers=headers, 
                    json=payload,
                    timeout=30  # Оптимальный таймаут для webhook сервера
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.debug(f"NeuroAPI response for chat {chat_id}: {result}")
                    assistant_message = result["choices"][0]["message"]["content"]
                    
                    # Если ответ не пустой, выходим из цикла
                    if assistant_message and assistant_message.strip():
                        break
                    else:
                        logger.warning(f"Empty response from NeuroAPI for chat {chat_id}, attempt {attempt + 1}")
                        if attempt < max_retries:
                            logger.info(f"Retrying request for chat {chat_id}, attempt {attempt + 2}")
                            continue
                else:
                    logger.error(f"NeuroAPI Error {response.status_code}: {response.text}")
                    # Если это не 200 статус, используем fallback
                    if is_business_message:
                        assistant_message = "Привет! Я ИИ-ассистент Сергея. Произошла техническая ошибка, но Сергей прочитает ваше сообщение и ответит как только сможет."
                    else:
                        assistant_message = f"Извините, произошла ошибка при обращении к GPT-5. Попробуйте позже."
                    break
                
            # Проверяем, что ответ не пустой (после всех попыток)
            if not assistant_message or not assistant_message.strip():
                logger.warning(f"Empty response from NeuroAPI for chat {chat_id} after {max_retries + 1} attempts")
                if is_business_message:
                    # Проверяем, есть ли контекст для этого чата
                    context_key = f"business_{business_connection_id}_{chat_id}"
                    if context_key in self.chat_contexts and len(self.chat_contexts[context_key]) > 0:
                        # Если контекст есть, используем более естественный ответ
                        assistant_message = "Сергей прочитает ваше сообщение и ответит как только сможет. Извините за задержку."
                    else:
                        # Если контекста нет, представляемся
                        assistant_message = "Привет! Я ИИ-ассистент Сергея. Он прочитает ваше сообщение и ответит как только сможет. Чем могу помочь?"
                else:
                    assistant_message = "Извините, я не смог сгенерировать ответ. Попробуйте еще раз."
            
            # Update context (для всех случаев - успешных и fallback)
            self._update_context(chat_id, user_message, assistant_message, is_business_message, business_connection_id)
            
            logger.info(f"Successfully got response from NeuroAPI GPT-5 for chat {chat_id} ({message_type}): {assistant_message[:100]}...")
            return assistant_message
                
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

def get_gpt_response(user_message: str, chat_id: int = 0, is_business_message: bool = False, business_connection_id: str = None) -> str:
    """Backward compatibility function"""
    return neuroapi_client.get_response(user_message, chat_id, is_business_message, business_connection_id)
