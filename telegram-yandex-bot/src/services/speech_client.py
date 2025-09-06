import requests
import logging
from typing import Optional
from config import config
from .iam_token_manager import token_manager

logger = logging.getLogger(__name__)

class SpeechClient:
    def __init__(self):
        self.api_key = config.YC_API_KEY
        self.iam_token = config.YC_IAM_TOKEN
        self.folder_id = config.YC_FOLDER_ID
        self.stt_endpoint = config.YC_STT_ENDPOINT
        self.tts_endpoint = config.YC_TTS_ENDPOINT
        # HTTP session with retries
        self.session = requests.Session()
        try:
            from requests.adapters import HTTPAdapter
            from urllib3.util import Retry
            retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
            self.session.mount("https://", HTTPAdapter(max_retries=retries))
        except Exception:
            pass
        
    def _get_auth_header(self) -> str:
        """Get authentication header value"""
        if self.api_key:
            return f"Api-Key {self.api_key}"
        elif self.iam_token:
            return f"Bearer {self.iam_token}"
        else:
            raise ValueError("Either YC_API_KEY or YC_IAM_TOKEN must be provided")
    
    def speech_to_text(self, audio_data: bytes, language: str = None) -> Optional[str]:
        """Convert speech to text using Yandex SpeechKit STT"""
        if not config.ENABLE_VOICE:
            return None
            
        try:
            language = language or config.STT_LANGUAGE
            
            # Prefer static creds; auto IAM only if SA key configured
            if self.iam_token:
                auth_header = f"Bearer {self.iam_token}"
            elif self.api_key:
                auth_header = f"Api-Key {self.api_key}"
            elif config.YC_SA_KEY_FILE or config.YC_SA_KEY_JSON:
                iam = token_manager.get_token()
                auth_header = f"Bearer {iam}"
            else:
                auth_header = self._get_auth_header()
            headers = {"Authorization": auth_header}
            
            params = {
                "folderId": self.folder_id,
                "lang": language,
                "topic": "general",
                "profanityFilter": "false"
            }
            
            logger.info(f"Sending STT request, audio size: {len(audio_data)} bytes")
            
            response = requests.post(
                self.stt_endpoint,
                headers=headers,
                params=params,
                data=audio_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                recognized_text = result.get("result", "")
                logger.info(f"STT successful, recognized: '{recognized_text[:50]}...'")
                return recognized_text
            else:
                logger.error(f"STT API Error {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("STT timeout error")
            return None
        except Exception as e:
            logger.error(f"STT unexpected error: {str(e)}")
            return None
    
    def text_to_speech(self, text: str, voice: str = None, language: str = None) -> Optional[bytes]:
        """Convert text to speech using Yandex SpeechKit TTS"""
        if not config.ENABLE_VOICE:
            return None
            
        try:
            voice = voice or config.TTS_VOICE
            # Determine language from voice if not specified
            if not language:
                if voice in ["alena", "jane", "omazh", "zahar", "ermil"]:
                    language = "ru-RU"
                else:
                    language = "en-US"
            
            # Prefer static creds; auto IAM only if SA key configured
            if self.iam_token:
                auth_header = f"Bearer {self.iam_token}"
            elif self.api_key:
                auth_header = f"Api-Key {self.api_key}"
            elif config.YC_SA_KEY_FILE or config.YC_SA_KEY_JSON:
                iam = token_manager.get_token()
                auth_header = f"Bearer {iam}"
            else:
                auth_header = self._get_auth_header()
            headers = {"Authorization": auth_header, "Content-Type": "application/x-www-form-urlencoded"}
            
            data = {
                "text": text,
                "lang": language,
                "voice": voice,
                "format": config.TTS_FORMAT,
                "speed": "1.0",
                "folderId": self.folder_id
            }
            
            logger.info(f"Sending TTS request, text length: {len(text)}")
            
            response = requests.post(
                self.tts_endpoint,
                headers=headers,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"TTS successful, audio size: {len(response.content)} bytes")
                return response.content
            else:
                logger.error(f"TTS API Error {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("TTS timeout error")
            return None
        except Exception as e:
            logger.error(f"TTS unexpected error: {str(e)}")
            return None

# Global client instance
speech_client = SpeechClient()