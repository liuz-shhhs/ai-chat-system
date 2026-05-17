from fastapi import APIRouter

from model.chat_model import ConversationCreateRequest
from service.conversation_service import create_new_conversation

router = APIRouter()


@router.post("/conversations")
def create_conversation(req: ConversationCreateRequest):
    user_id = 1
    conversation_id = create_new_conversation(user_id, req.title)

    return {
        "id": conversation_id,
        "title": req.title or "新对话",
    }
