import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from requests import RequestException

from model.chat_model import ChatRequest
from service.chat_service import chat_with_ai, stream_chat_with_ai

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


@router.post("/chat/stream")
def chat_stream(req: ChatRequest):
    user_id = 1

    return StreamingResponse(
        stream_events(user_id, req),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


def stream_events(user_id, req):
    try:
        for event in stream_chat_with_ai(user_id, req.conversation_id, req.message):
            event_type = event.pop("type")
            yield format_sse(event_type, event)
    except RequestException as exc:
        yield format_sse("error", {"message": f"AI 服务调用失败: {exc}"})
    except ValueError as exc:
        yield format_sse("error", {"message": str(exc)})
    except Exception as exc:
        yield format_sse("error", {"message": f"流式回复失败: {exc}"})


def format_sse(event, data):
    payload = json.dumps(data, ensure_ascii=False)
    return f"event: {event}\ndata: {payload}\n\n"
