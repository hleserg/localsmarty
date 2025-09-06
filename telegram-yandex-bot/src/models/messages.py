from pydantic import BaseModel

class UserMessage(BaseModel):
    user_id: str
    text: str

class BotResponse(BaseModel):
    response_text: str
    is_typing: bool = False

class ErrorMessage(BaseModel):
    error: str
    code: int