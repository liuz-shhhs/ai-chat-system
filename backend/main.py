

from fastapi import FastAPI
from pydantic import BaseModel
import pymysql
import requests
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发阶段先用 *
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== 配置 ==========
DEEPSEEK_API_KEY = "sk-5d3f121f6f3a44a39c22d44a7045f8e7"

def get_conn():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="2191717",   # ← 改这里
        database="chat_db",
        charset="utf8mb4"
    )

# ========== 请求模型 ==========
class ChatRequest(BaseModel):
    message: str

# ========== 存消息 ==========
def save_message(user_id, role, content):
    conn = get_conn()
    cursor = conn.cursor()

    sql = """
    INSERT INTO messages (user_id, role, content)
    VALUES (%s, %s, %s)
    """

    cursor.execute(sql, (user_id, role, content))
    conn.commit()
    conn.close()

# ========== 取历史 ==========
def load_messages(user_id):
    conn = get_conn()
    cursor = conn.cursor()

    sql = """
    SELECT role, content FROM messages
    WHERE user_id = %s
    ORDER BY id ASC
    """

    cursor.execute(sql, (user_id,))
    rows = cursor.fetchall()
    conn.close()

    return [
        {"role": r[0], "content": r[1]}
        for r in rows
    ]

# ========== 基础接口 ==========
@app.get("/")
def root():
    return {"message": "AI Chat System Running"}

# ========== 核心AI接口 ==========
@app.post("/chat")
def chat(req: ChatRequest):

    user_id = 1
    user_input = req.message

    # 1. 存用户消息
    save_message(user_id, "user", user_input)

    # 2. 取历史消息
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

    # 5. 存AI回复
    save_message(user_id, "assistant", ai_reply)

    return {
        "user_input": user_input,
        "answer": ai_reply
    }