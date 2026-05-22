from dao.db import get_conn


def create_conversation(user_id, title):
    conn = get_conn()
    cursor = conn.cursor()

    sql = """
    INSERT INTO conversations (user_id, title)
    VALUES (%s, %s)
    """

    cursor.execute(sql, (user_id, title))
    conn.commit()
    conversation_id = cursor.lastrowid
    conn.close()

    return conversation_id


def get_conversations(user_id):
    conn = get_conn()
    cursor = conn.cursor()

    sql = """
    SELECT id, title, created_at
    FROM conversations
    WHERE user_id = %s
    ORDER BY id DESC
    """

    cursor.execute(sql, (user_id,))
    rows = cursor.fetchall()

    conn.close()

    return [
        {"id": r[0], "title": r[1], "created_at": str(r[2])}
        for r in rows
    ]


def delete_conversation(user_id, conversation_id):
    conn = get_conn()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            DELETE FROM messages
            WHERE user_id = %s AND conversation_id = %s
            """,
            (user_id, conversation_id),
        )

        cursor.execute(
            """
            DELETE FROM conversations
            WHERE user_id = %s AND id = %s
            """,
            (user_id, conversation_id),
        )

        deleted = cursor.rowcount
        conn.commit()
        return deleted > 0
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
