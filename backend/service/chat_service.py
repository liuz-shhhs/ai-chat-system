import requests

from config.settings import DEEPSEEK_API_KEY
from dao.message_dao import save_message, load_messages
from service.conversation_service import create_new_conversation


def chat_with_ai(user_id, conversation_id, user_input):
    if not DEEPSEEK_API_KEY:
        raise ValueError("缺少 DEEPSEEK_API_KEY，请在 .env 中配置。")

    if conversation_id is None:
        title = user_input[:20] if user_input else "新对话"
        conversation_id = create_new_conversation(user_id, title)

    # 1. 保存用户消息
    save_message(user_id, conversation_id, "user", user_input)

    # 2. 读取历史消息
    messages = load_messages(conversation_id)

    # 3. 调用大模型
    response = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "deepseek-chat",
            "messages": messages
        },
        timeout=60,
    )
    response.raise_for_status()

    result = response.json()

    # 4. 解析AI回复
    ai_reply = result.get("choices", [{}])[0].get("message", {}).get("content")
    if not ai_reply:
        raise ValueError("AI 接口返回格式异常，未找到回复内容。")

    # 5. 保存AI回复
    save_message(user_id, conversation_id, "assistant", ai_reply)

    return {
        "answer": ai_reply,
        "conversation_id": conversation_id,
    }
