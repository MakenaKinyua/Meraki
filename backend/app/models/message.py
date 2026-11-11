from datetime import datetime, timezone
from uuid import uuid4

from app.database import session


def create(conversation_id: str, role: str, content: str) -> dict:
    message = {
        "id": str(uuid4()),
        "conversation_id": conversation_id,
        "role": role,
        "content": content,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    with session() as connection:
        connection.execute(
            """INSERT INTO messages (id, conversation_id, role, content, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (
                message["id"],
                message["conversation_id"],
                message["role"],
                message["content"],
                message["created_at"],
            ),
        )
    return message


def for_conversation(conversation_id: str) -> list[dict]:
    with session() as connection:
        rows = connection.execute(
            """SELECT id, conversation_id, role, content, created_at
               FROM messages WHERE conversation_id = ?
               ORDER BY created_at, rowid""",
            (conversation_id,),
        ).fetchall()
    return [dict(row) for row in rows]
