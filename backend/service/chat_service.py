import requests

from config.settings import DEEPSEEK_API_KEY
from dao.message_dao import save_message, load_messages


def chat_with_ai(user_id, user_input):

    # 1. 保存用户消息
    save_message(user_id, "user", user_input)

    # 2. 读取历史消息
    messages = load_messages(user_id)

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
        }
    )

    result = response.json()

    # 4. 解析AI回复
    ai_reply = result["choices"][0]["message"]["content"]

    # 5. 保存AI回复
    save_message(user_id, "assistant", ai_reply)

    return ai_reply