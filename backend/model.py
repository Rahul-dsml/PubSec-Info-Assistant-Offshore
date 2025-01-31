from pydantic import BaseModel
from typing import Optional

class ChatResponse(BaseModel):
    user_query    : str
    chat_history  : list[dict]
    chat_language : str

class GetDetails(BaseModel):
    apartment_id   : str