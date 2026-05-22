import json

import requests

from config.settings import DEEPSEEK_API_KEY
from dao.message_dao import save_message, load_messages
from service.rag_service import (
    build_rag_system_message,
    retrieve_relevant_chunks,
    serialize_sources,
)
from service.conversation_service import create_new_conversation


def prepare_chat_context(user_id, conversation_id, user_input):
    if not DEEPSEEK_API_KEY:
        raise ValueError("缺少 DEEPSEEK_API_KEY，请在 .env 中配置。")

    if conversation_id is None:
        title = user_input[:20] if user_input else "新对话"
        conversation_id = create_new_conversation(user_id, title)

    # 1. 保存用户消息
    save_message(user_id, conversation_id, "user", user_input)

    # 2. 读取历史消息
    messages = load_messages(conversation_id)

    # 3. 检索用户上传文档中的相关片段
    try:
        sources = retrieve_relevant_chunks(user_id, user_input)
    except Exception:
        sources = []

    rag_system_message = build_rag_system_message(sources)

    if rag_system_message:
        messages = [rag_system_message] + messages

    return conversation_id, messages, sources


def chat_with_ai(user_id, conversation_id, user_input):
    conversation_id, messages, sources = prepare_chat_context(
        user_id,
        conversation_id,
        user_input,
    )

    # 4. 调用大模型
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

    # 5. 解析AI回复
    ai_reply = result.get("choices", [{}])[0].get("message", {}).get("content")
    if not ai_reply:
        raise ValueError("AI 接口返回格式异常，未找到回复内容。")

    # 6. 保存AI回复
    save_message(user_id, conversation_id, "assistant", ai_reply)

    return {
        "answer": ai_reply,
        "conversation_id": conversation_id,
        "sources": serialize_sources(sources),
    }


def stream_chat_with_ai(user_id, conversation_id, user_input):
    conversation_id, messages, sources = prepare_chat_context(
        user_id,
        conversation_id,
        user_input,
    )
    serialized_sources = serialize_sources(sources)

    yield {
        "type": "start",
        "conversation_id": conversation_id,
        "sources": serialized_sources,
    }

    response = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "deepseek-chat",
            "messages": messages,
            "stream": True,
        },
        stream=True,
        timeout=60,
    )
    response.raise_for_status()

    answer_parts = []

    for line in response.iter_lines(decode_unicode=True):
        data = parse_stream_line(line)

        if data is None:
            continue

        if data == "[DONE]":
            break

        chunk = json.loads(data)
        delta = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")

        if delta:
            answer_parts.append(delta)
            yield {
                "type": "delta",
                "content": delta,
            }

    ai_reply = "".join(answer_parts).strip()

    if not ai_reply:
        raise ValueError("AI 接口返回格式异常，未找到回复内容。")

    save_message(user_id, conversation_id, "assistant", ai_reply)

    yield {
        "type": "done",
        "conversation_id": conversation_id,
        "sources": serialized_sources,
    }


def parse_stream_line(line):
    if not line:
        return None

    if isinstance(line, bytes):
        line = line.decode("utf-8")

    line = line.strip()

    if not line.startswith("data:"):
        return None

    return line[5:].strip()
