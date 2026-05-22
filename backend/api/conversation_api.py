from fastapi import APIRouter, HTTPException

from service.conversation_service import delete_user_conversation, list_conversations

router = APIRouter()


@router.get("/conversations")
def get_conversations():

    user_id = 1

    data = list_conversations(user_id)

    return {
        "data": data
    }


@router.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: int):
    user_id = 1

    deleted = delete_user_conversation(user_id, conversation_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="会话不存在或无权删除。")

    return {
        "deleted": True,
        "id": conversation_id,
    }
