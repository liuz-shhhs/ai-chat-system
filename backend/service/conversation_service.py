from dao.conversation_dao import get_conversations


def list_conversations(user_id):
    return get_conversations(user_id)