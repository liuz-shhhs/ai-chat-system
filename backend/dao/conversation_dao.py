from dao.db import get_conn


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