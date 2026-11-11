import os
import sqlite3
from contextlib import closing, contextmanager
from pathlib import Path
from collections.abc import Iterator

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHAT_DATABASE_PATH = Path(os.getenv("CHAT_DB_PATH", PROJECT_ROOT / "data" / "chat.db"))


def connect() -> sqlite3.Connection:
    CHAT_DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(CHAT_DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def session() -> Iterator[sqlite3.Connection]:
    with closing(connect()) as connection:
        with connection:
            yield connection


def initialize_database() -> None:
    with session() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_messages_conversation
                ON messages(conversation_id, created_at, id);
            """
        )
