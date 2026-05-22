from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.chat_api import router as chat_router
from api.conversation_api import router as conversation_router
from api.conversation_create_api import router as conversation_create_router
from api.document_api import router as document_router

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat_router)
app.include_router(conversation_router)
app.include_router(conversation_create_router)
app.include_router(document_router)


@app.get("/")
def root():
    return {"message": "AI Chat System Running"}
