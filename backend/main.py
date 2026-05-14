from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

class ChatRequest(BaseModel):
    message: str


DEEPSEEK_API_KEY = "sk-5d3f121f6f3a44a39c22d44a7045f8e7"


@app.post("/chat")
def chat(req: ChatRequest):

    user_input = req.message

    # 1. 构造messages（你之前问过这个）
    messages = [
        {"role": "user", "content": user_input}
    ]

    # 2. 调用大模型API
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

    # 3. 提取AI回复
    ai_reply = result["choices"][0]["message"]["content"]

    return {
        "user_input": user_input,
        "answer": ai_reply
    }