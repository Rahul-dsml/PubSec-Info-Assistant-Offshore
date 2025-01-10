from pydantic import BaseModel
from typing import Optional

class ChatResponse(BaseModel):
    user_query    : str
    chat_history  : list[str]
    chat_language : str
