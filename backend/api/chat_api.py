from fastapi import APIRouter

from model.chat_model import ChatRequest
from service.chat_service import chat_with_ai

router = APIRouter()


@router.post("/chat")
def chat(req: ChatRequest):

    user_id = 1

    ai_reply = chat_with_ai(user_id, req.message)

    return {
        "answer": ai_reply
    }