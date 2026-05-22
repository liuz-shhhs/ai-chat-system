import math
import re
from collections import Counter
from pathlib import Path

from dao.document_dao import (
    delete_document,
    load_document_chunks,
    list_documents,
    save_document_with_chunks,
)
from service.document_parser import (
    clean_filename,
    chunk_sections,
    decode_base64_file,
    extract_sections,
)


TOP_K = 4
SOURCE_PREVIEW_CHARS = 180


def ingest_document(user_id, filename, content_base64, content_type=None):
    clean_name = clean_filename(filename)
    content = decode_base64_file(content_base64)
    sections = extract_sections(clean_name, content)
    chunks = chunk_sections(sections)
    file_type = (Path(clean_name).suffix.lower().lstrip(".") or content_type or "text")[:32]
    document_id = save_document_with_chunks(user_id, clean_name, file_type, chunks)

    return {
        "id": document_id,
        "filename": clean_name,
        "file_type": file_type,
        "chunk_count": len(chunks),
    }


def get_user_documents(user_id):
    return list_documents(user_id)


def delete_user_document(user_id, document_id):
    return delete_document(user_id, document_id)


def retrieve_relevant_chunks(user_id, query, limit=TOP_K):
    chunks = load_document_chunks(user_id)
    query_vector = build_vector(query)

    if not query_vector:
        return []

    scored_chunks = []

    for chunk in chunks:
        content = chunk["content"]
        candidate_vector = build_vector(f"{chunk['filename']}\n{content}")
        score = cosine_similarity(query_vector, candidate_vector)

        if contains_query_phrase(query, content):
            score += 0.18

        if score > 0:
            scored_chunks.append((score, chunk))

    scored_chunks.sort(key=lambda item: item[0], reverse=True)

    return [
        {
            **chunk,
            "score": round(score, 4),
            "preview": build_preview(chunk["content"]),
        }
        for score, chunk in scored_chunks[:limit]
    ]


def build_rag_system_message(sources):
    if not sources:
        return None

    lines = [
        "你是一个严谨的文档问答助手。",
        "回答时优先依据下方检索到的用户文档片段；如果片段不足以支持结论，请明确说明资料不足。",
        "不要编造文档中没有的信息。回答末尾用“参考来源”列出使用到的文件名。",
        "",
        "检索到的文档片段：",
    ]

    for index, source in enumerate(sources, start=1):
        page = f" 第 {source['page_number']} 页" if source.get("page_number") else ""
        lines.extend(
            [
                "",
                f"[来源 {index}] {source['filename']}{page} / 片段 {source['chunk_index'] + 1}",
                source["content"],
            ]
        )

    return {
        "role": "system",
        "content": "\n".join(lines),
    }


def serialize_sources(sources):
    return [
        {
            "document_id": source["document_id"],
            "filename": source["filename"],
            "page_number": source.get("page_number"),
            "chunk_index": source["chunk_index"],
            "score": source["score"],
            "preview": source["preview"],
        }
        for source in sources
    ]


def build_vector(text):
    return Counter(tokenize(text))


def tokenize(text):
    tokens = []

    for match in re.finditer(r"[\u4e00-\u9fff]+|[a-z0-9]+", (text or "").lower()):
        piece = match.group(0)

        if re.fullmatch(r"[\u4e00-\u9fff]+", piece):
            tokens.extend(piece)
            tokens.extend(
                piece[index:index + 2]
                for index in range(len(piece) - 1)
            )
        elif len(piece) > 1:
            tokens.append(piece)

    return tokens


def cosine_similarity(left, right):
    if not left or not right:
        return 0

    overlap = set(left) & set(right)
    numerator = sum(left[token] * right[token] for token in overlap)
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))

    if not left_norm or not right_norm:
        return 0

    return numerator / (left_norm * right_norm)


def contains_query_phrase(query, content):
    normalized_query = re.sub(r"\s+", "", query or "").lower()
    normalized_content = re.sub(r"\s+", "", content or "").lower()

    return len(normalized_query) >= 4 and normalized_query in normalized_content


def build_preview(content):
    preview = re.sub(r"\s+", " ", content or "").strip()

    if len(preview) <= SOURCE_PREVIEW_CHARS:
        return preview

    return f"{preview[:SOURCE_PREVIEW_CHARS]}..."
