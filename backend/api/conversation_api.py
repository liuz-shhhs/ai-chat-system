from fastapi import APIRouter

from service.conversation_service import list_conversations

router = APIRouter()


@router.get("/conversations")
def get_conversations():

    user_id = 1

    data = list_conversations(user_id)

    return {
        "data": data
    }