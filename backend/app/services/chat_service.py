from src.explanations.generator import explain_ingredient

from app.models import conversation, message


def create_conversation() -> dict:
    return {**conversation.create(), "title": None, "messages": []}


def list_conversations() -> list[dict]:
    return conversation.list_all()


def get_conversation(conversation_id: str) -> dict | None:
    record = conversation.find(conversation_id)
    if record is None:
        return None
    return {**record, "messages": message.for_conversation(conversation_id)}


def answer_question(conn,question: str) -> str:
    result = explain_ingredient(conn,question)
    if result.status == "not_found":
        return f"No match found for '{question}'."
    if result.status == "ok" and result.explanation:
        return result.explanation
    raise RuntimeError(result.error or "Ingredient explanation failed")
