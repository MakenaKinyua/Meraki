from datetime import datetime, timezone
from uuid import uuid4

from app.database import session


def create() -> dict:
    conversation = {
        "id": str(uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    with session() as connection:
        connection.execute(
            "INSERT INTO conversations (id, created_at) VALUES (?, ?)",
            (conversation["id"], conversation["created_at"]),
        )
    return conversation


def find(conversation_id: str) -> dict | None:
    with session() as connection:
        row = connection.execute(
            """SELECT c.id, c.created_at,
                      (SELECT content FROM messages
                       WHERE conversation_id = c.id AND role = 'user'
                       ORDER BY rowid LIMIT 1) AS title
               FROM conversations c WHERE c.id = ?""",
            (conversation_id,),
        ).fetchone()
    return dict(row) if row else None


def list_all() -> list[dict]:
    with session() as connection:
        rows = connection.execute(
            """SELECT c.id, c.created_at,
                      (SELECT content FROM messages
                       WHERE conversation_id = c.id AND role = 'user'
                       ORDER BY rowid LIMIT 1) AS title
               FROM conversations c ORDER BY c.created_at DESC"""
        ).fetchall()
    return [dict(row) for row in rows]
