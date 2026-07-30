"""
Persistent conversation memory using SQLite.

Stores conversations by Telegram user ID.

Automatically keeps only the most recent N messages per user.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from datetime import datetime

DB_FILE = Path("memory.db")

MAX_MESSAGES = 20


class ConversationMemory:

    def __init__(self):

        self.conn = sqlite3.connect(
            DB_FILE,
            check_same_thread=False,
        )

        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages(

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id TEXT NOT NULL,

                role TEXT NOT NULL,

                message TEXT NOT NULL,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        self.conn.commit()

    # ---------------------------------------------

    def add_message(
        self,
        user_id: str,
        role: str,
        message: str,
    ):

        self.conn.execute(
            """
            INSERT INTO messages(
                user_id,
                role,
                message
            )
            VALUES(?,?,?)
            """,
            (
                str(user_id),
                role,
                message,
            ),
        )

        self.conn.commit()

        self.trim(user_id)

    # ---------------------------------------------

    def trim(self, user_id: str):

        cursor = self.conn.execute(
            """
            SELECT id
            FROM messages
            WHERE user_id=?
            ORDER BY id DESC
            """,
            (str(user_id),),
        )

        ids = [row[0] for row in cursor.fetchall()]

        if len(ids) <= MAX_MESSAGES:
            return

        remove = ids[MAX_MESSAGES:]

        self.conn.executemany(
            "DELETE FROM messages WHERE id=?",
            [(i,) for i in remove],
        )

        self.conn.commit()

    # ---------------------------------------------

    def history(self, user_id: str):

        cursor = self.conn.execute(
            """
            SELECT role,message

            FROM messages

            WHERE user_id=?

            ORDER BY id ASC
            """,
            (str(user_id),),
        )

        return cursor.fetchall()

    # ---------------------------------------------

    def formatted_history(self, user_id: str):

        rows = self.history(user_id)

        if not rows:
            return ""

        lines = []

        for role, message in rows:

            lines.append(
                f"{role.upper()}: {message}"
            )

        return "\n".join(lines)

    # ---------------------------------------------

    def clear(self, user_id: str):

        self.conn.execute(
            """
            DELETE FROM messages

            WHERE user_id=?
            """,
            (str(user_id),),
        )

        self.conn.commit()

    # ---------------------------------------------

    def close(self):

        self.conn.close()


memory = ConversationMemory()
