from dao.db import get_conn


def ensure_document_tables():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            id INT PRIMARY KEY AUTO_INCREMENT,
            user_id INT NOT NULL,
            filename VARCHAR(255) NOT NULL,
            file_type VARCHAR(32) NOT NULL,
            chunk_count INT NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_documents_user_id (user_id)
        )
        """
    )

    cursor.execute(
        """
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
        )
        """
    )

    conn.commit()
    conn.close()


def save_document_with_chunks(user_id, filename, file_type, chunks):
    ensure_document_tables()

    conn = get_conn()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO documents (user_id, filename, file_type, chunk_count)
            VALUES (%s, %s, %s, %s)
            """,
            (user_id, filename, file_type, len(chunks)),
        )
        document_id = cursor.lastrowid

        sql = """
        INSERT INTO document_chunks
            (document_id, user_id, chunk_index, content, page_number)
        VALUES (%s, %s, %s, %s, %s)
        """

        for chunk in chunks:
            cursor.execute(
                sql,
                (
                    document_id,
                    user_id,
                    chunk["chunk_index"],
                    chunk["content"],
                    chunk.get("page_number"),
                ),
            )

        conn.commit()
        return document_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def list_documents(user_id):
    ensure_document_tables()

    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, filename, file_type, chunk_count, created_at
        FROM documents
        WHERE user_id = %s
        ORDER BY id DESC
        """,
        (user_id,),
    )
    rows = cursor.fetchall()

    conn.close()

    return [
        {
            "id": row[0],
            "filename": row[1],
            "file_type": row[2],
            "chunk_count": row[3],
            "created_at": str(row[4]),
        }
        for row in rows
    ]


def load_document_chunks(user_id):
    ensure_document_tables()

    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            c.id,
            c.document_id,
            d.filename,
            c.chunk_index,
            c.content,
            c.page_number
        FROM document_chunks c
        INNER JOIN documents d ON d.id = c.document_id
        WHERE c.user_id = %s
        ORDER BY d.id DESC, c.chunk_index ASC
        """,
        (user_id,),
    )
    rows = cursor.fetchall()

    conn.close()

    return [
        {
            "id": row[0],
            "document_id": row[1],
            "filename": row[2],
            "chunk_index": row[3],
            "content": row[4],
            "page_number": row[5],
        }
        for row in rows
    ]


def delete_document(user_id, document_id):
    ensure_document_tables()

    conn = get_conn()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            DELETE FROM document_chunks
            WHERE user_id = %s AND document_id = %s
            """,
            (user_id, document_id),
        )

        cursor.execute(
            """
            DELETE FROM documents
            WHERE user_id = %s AND id = %s
            """,
            (user_id, document_id),
        )

        deleted = cursor.rowcount
        conn.commit()
        return deleted > 0
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
