from dao.conversation_dao import create_conversation, delete_conversation, get_conversations


def create_new_conversation(user_id, title=None):
    clean_title = (title or "新对话").strip() or "新对话"
    return create_conversation(user_id, clean_title)


def list_conversations(user_id):
    return get_conversations(user_id)


def delete_user_conversation(user_id, conversation_id):
    return delete_conversation(user_id, conversation_id)
