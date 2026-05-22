# AI Chat System

一个 FastAPI + MySQL + 原生前端的 AI 聊天项目，支持基础文档解析 RAG。

## 环境变量

在项目根目录创建 `.env`：

```env
DEEPSEEK_API_KEY=你的 DeepSeek API Key
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=你的 MySQL 密码
MYSQL_DATABASE=chat_db
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 数据库表

```sql
CREATE DATABASE IF NOT EXISTS chat_db DEFAULT CHARACTER SET utf8mb4;
USE chat_db;

CREATE TABLE IF NOT EXISTS conversations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS messages (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    conversation_id INT NOT NULL,
    role VARCHAR(32) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_messages_conversation_id (conversation_id)
);

CREATE TABLE IF NOT EXISTS documents (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(32) NOT NULL,
    chunk_count INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_documents_user_id (user_id)
);

CREATE TABLE IF NOT EXISTS document_chunks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    document_id INT NOT NULL,
    user_id INT NOT NULL,
    chunk_index INT NOT NULL,
    content TEXT NOT NULL,
    page_number INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_document_chunks_user_id (user_id),
    INDEX idx_document_chunks_document_id (document_id),
    CONSTRAINT fk_document_chunks_document_id
        FOREIGN KEY (document_id)
        REFERENCES documents(id)
        ON DELETE CASCADE
);
```

同样的建表脚本也放在 `docs/schema.sql`。

## 文档 RAG

前端可以上传 TXT、Markdown、CSV、DOCX 和 PDF 文档。后端会解析文本、切块并保存到 MySQL，聊天时自动检索相关片段注入模型上下文，并在回答中返回引用来源。

PDF 解析依赖 `pypdf`，安装依赖时会一起安装：

```bash
pip install -r requirements.txt
```

## SSE 流式输出

前端聊天默认请求 `POST /chat/stream`，后端以 `text/event-stream` 返回以下事件：

- `start`：返回 `conversation_id` 和命中的文档来源。
- `delta`：返回本次增量文本。
- `done`：回复结束，并返回最终会话和来源信息。
- `error`：流式调用失败时返回错误消息。

原来的 `POST /chat` 保留为非流式接口，方便兼容旧调用。

## 删除数据

前端支持删除会话和删除 RAG 文档：

- `DELETE /conversations/{conversation_id}`：删除会话及其消息。
- `DELETE /documents/{document_id}`：删除文档及其检索片段。

删除文档只影响后续检索，不会改写已经生成过的聊天回答。

## 启动后端

```bash
cd backend
uvicorn main:app --reload
```

然后用浏览器打开 `frontend/index.html`。
