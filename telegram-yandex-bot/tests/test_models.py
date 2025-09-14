"""
Тесты для моделей данных.
"""
import pytest
import sys
import os
from pydantic import ValidationError

# Добавляем src в путь для импортов
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from models.messages import UserMessage, BotResponse, ErrorMessage


@pytest.mark.models
class TestModels:
    """Тесты для моделей данных"""

    def test_user_message_creation(self):
        """Тест создания UserMessage"""
        user_msg = UserMessage(user_id="123", text="Тестовое сообщение")
        
        assert user_msg.user_id == "123"
        assert user_msg.text == "Тестовое сообщение"

    def test_user_message_validation(self):
        """Тест валидации UserMessage"""
        # Валидные данные
        user_msg = UserMessage(user_id="123", text="Тест")
        assert user_msg.user_id == "123"
        assert user_msg.text == "Тест"
        
        # Невалидные данные - отсутствует обязательное поле
        with pytest.raises(ValidationError):
            UserMessage(user_id="123")  # Отсутствует text
        
        with pytest.raises(ValidationError):
            UserMessage(text="Тест")  # Отсутствует user_id

    def test_user_message_empty_text(self):
        """Тест UserMessage с пустым текстом"""
        user_msg = UserMessage(user_id="123", text="")
        assert user_msg.text == ""

    def test_user_message_long_text(self):
        """Тест UserMessage с длинным текстом"""
        long_text = "A" * 1000
        user_msg = UserMessage(user_id="123", text=long_text)
        assert user_msg.text == long_text

    def test_user_message_unicode_text(self):
        """Тест UserMessage с Unicode текстом"""
        unicode_text = "Привет, мир! 🌍 Тест с эмодзи 😊"
        user_msg = UserMessage(user_id="123", text=unicode_text)
        assert user_msg.text == unicode_text

    def test_bot_response_creation(self):
        """Тест создания BotResponse"""
        bot_resp = BotResponse(response_text="Ответ бота")
        
        assert bot_resp.response_text == "Ответ бота"
        assert bot_resp.is_typing is False  # Значение по умолчанию

    def test_bot_response_with_typing(self):
        """Тест BotResponse с typing статусом"""
        bot_resp = BotResponse(response_text="Ответ", is_typing=True)
        
        assert bot_resp.response_text == "Ответ"
        assert bot_resp.is_typing is True

    def test_bot_response_validation(self):
        """Тест валидации BotResponse"""
        # Валидные данные
        bot_resp = BotResponse(response_text="Тест")
        assert bot_resp.response_text == "Тест"
        
        # Невалидные данные - отсутствует обязательное поле
        with pytest.raises(ValidationError):
            BotResponse()  # Отсутствует response_text

    def test_bot_response_empty_text(self):
        """Тест BotResponse с пустым текстом"""
        bot_resp = BotResponse(response_text="")
        assert bot_resp.response_text == ""

    def test_bot_response_long_text(self):
        """Тест BotResponse с длинным текстом"""
        long_text = "A" * 5000
        bot_resp = BotResponse(response_text=long_text)
        assert bot_resp.response_text == long_text

    def test_bot_response_unicode_text(self):
        """Тест BotResponse с Unicode текстом"""
        unicode_text = "Ответ: Привет! 🌟 Как дела? 😊"
        bot_resp = BotResponse(response_text=unicode_text)
        assert bot_resp.response_text == unicode_text

    def test_error_message_creation(self):
        """Тест создания ErrorMessage"""
        error_msg = ErrorMessage(error="Произошла ошибка", code=500)
        
        assert error_msg.error == "Произошла ошибка"
        assert error_msg.code == 500

    def test_error_message_validation(self):
        """Тест валидации ErrorMessage"""
        # Валидные данные
        error_msg = ErrorMessage(error="Тест", code=400)
        assert error_msg.error == "Тест"
        assert error_msg.code == 400
        
        # Невалидные данные - отсутствует обязательное поле
        with pytest.raises(ValidationError):
            ErrorMessage(code=500)  # Отсутствует error
        
        with pytest.raises(ValidationError):
            ErrorMessage(error="Тест")  # Отсутствует code

    def test_error_message_different_codes(self):
        """Тест ErrorMessage с разными кодами ошибок"""
        # HTTP коды ошибок
        error_400 = ErrorMessage(error="Bad Request", code=400)
        error_401 = ErrorMessage(error="Unauthorized", code=401)
        error_403 = ErrorMessage(error="Forbidden", code=403)
        error_404 = ErrorMessage(error="Not Found", code=404)
        error_500 = ErrorMessage(error="Internal Server Error", code=500)
        
        assert error_400.code == 400
        assert error_401.code == 401
        assert error_403.code == 403
        assert error_404.code == 404
        assert error_500.code == 500

    def test_error_message_empty_error(self):
        """Тест ErrorMessage с пустым сообщением об ошибке"""
        error_msg = ErrorMessage(error="", code=500)
        assert error_msg.error == ""

    def test_error_message_unicode_error(self):
        """Тест ErrorMessage с Unicode сообщением об ошибке"""
        unicode_error = "Ошибка: Произошла проблема с кодировкой 🚫"
        error_msg = ErrorMessage(error=unicode_error, code=500)
        assert error_msg.error == unicode_error

    def test_models_json_serialization(self):
        """Тест сериализации моделей в JSON"""
        user_msg = UserMessage(user_id="123", text="Тест")
        bot_resp = BotResponse(response_text="Ответ", is_typing=True)
        error_msg = ErrorMessage(error="Ошибка", code=500)
        
        # Проверяем что модели можно сериализовать в JSON
        user_json = user_msg.model_dump()
        bot_json = bot_resp.model_dump()
        error_json = error_msg.model_dump()
        
        assert user_json["user_id"] == "123"
        assert user_json["text"] == "Тест"
        
        assert bot_json["response_text"] == "Ответ"
        assert bot_json["is_typing"] is True
        
        assert error_json["error"] == "Ошибка"
        assert error_json["code"] == 500

    def test_models_json_deserialization(self):
        """Тест десериализации моделей из JSON"""
        user_data = {"user_id": "456", "text": "Тест из JSON"}
        bot_data = {"response_text": "Ответ из JSON", "is_typing": False}
        error_data = {"error": "Ошибка из JSON", "code": 404}
        
        # Создаем модели из данных
        user_msg = UserMessage(**user_data)
        bot_resp = BotResponse(**bot_data)
        error_msg = ErrorMessage(**error_data)
        
        assert user_msg.user_id == "456"
        assert user_msg.text == "Тест из JSON"
        
        assert bot_resp.response_text == "Ответ из JSON"
        assert bot_resp.is_typing is False
        
        assert error_msg.error == "Ошибка из JSON"
        assert error_msg.code == 404

    def test_models_type_validation(self):
        """Тест валидации типов данных"""
        # Проверяем что код ошибки должен быть числом
        with pytest.raises(ValidationError):
            ErrorMessage(error="Тест", code="не_число")
        
        # Проверяем что is_typing должен быть булевым значением
        with pytest.raises(ValidationError):
            BotResponse(response_text="Тест", is_typing="не_булево")

    def test_models_field_types(self):
        """Тест типов полей моделей"""
        user_msg = UserMessage(user_id="123", text="Тест")
        bot_resp = BotResponse(response_text="Ответ", is_typing=True)
        error_msg = ErrorMessage(error="Ошибка", code=500)
        
        # Проверяем типы полей
        assert isinstance(user_msg.user_id, str)
        assert isinstance(user_msg.text, str)
        
        assert isinstance(bot_resp.response_text, str)
        assert isinstance(bot_resp.is_typing, bool)
        
        assert isinstance(error_msg.error, str)
        assert isinstance(error_msg.code, int)

    def test_models_immutability(self):
        """Тест неизменяемости моделей"""
        user_msg = UserMessage(user_id="123", text="Тест")
        
        # Попытка изменить поле должна вызвать ошибку
        with pytest.raises(ValidationError):
            user_msg.user_id = "456"

    def test_models_str_representation(self):
        """Тест строкового представления моделей"""
        user_msg = UserMessage(user_id="123", text="Тест")
        bot_resp = BotResponse(response_text="Ответ", is_typing=True)
        error_msg = ErrorMessage(error="Ошибка", code=500)
        
        # Проверяем что модели имеют строковое представление
        assert str(user_msg) is not None
        assert str(bot_resp) is not None
        assert str(error_msg) is not None
        
        # Проверяем что строковое представление содержит ключевую информацию
        assert "123" in str(user_msg)
        assert "Ответ" in str(bot_resp)
        assert "Ошибка" in str(error_msg)

