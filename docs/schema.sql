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
