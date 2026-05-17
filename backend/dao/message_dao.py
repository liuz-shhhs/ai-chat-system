from dao.db import get_conn


def save_message(user_id, conversation_id, role, content):
    conn = get_conn()
    cursor = conn.cursor()

    sql = """
    INSERT INTO messages (user_id, conversation_id, role, content)
    VALUES (%s, %s, %s, %s)
    """

    cursor.execute(sql, (user_id, conversation_id, role, content))

    conn.commit()
    conn.close()


def load_messages(conversation_id):
    conn = get_conn()
    cursor = conn.cursor()

    sql = """
    SELECT role, content
    FROM messages
    WHERE conversation_id = %s
    ORDER BY id ASC
    """

    cursor.execute(sql, (conversation_id,))
    rows = cursor.fetchall()

    conn.close()

    return [
        {"role": r[0], "content": r[1]}
        for r in rows
    ]
