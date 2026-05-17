from fastapi import APIRouter, HTTPException
from requests import RequestException

from model.chat_model import ChatRequest
from service.chat_service import chat_with_ai

router = APIRouter()


@router.post("/chat")
def chat(req: ChatRequest):

    user_id = 1

    try:
        result = chat_with_ai(user_id, req.conversation_id, req.message)
    except RequestException as exc:
        raise HTTPException(status_code=502, detail=f"AI 服务调用失败: {exc}") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return result
