from typing import Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None


class ConversationCreateRequest(BaseModel):
    title: Optional[str] = None
