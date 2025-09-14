# Copyright © 2025, Alexander Suvorov
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional


class CLMDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")

            conn.execute('''
                CREATE TABLE IF NOT EXISTS config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS chats (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    seed_suffix TEXT NOT NULL,
                    created_at INTEGER DEFAULT (strftime('%s', 'now'))
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    chat_id TEXT NOT NULL,
                    epoch_index INTEGER NOT NULL,
                    message TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    timestamp INTEGER NOT NULL,
                    datetime TEXT NOT NULL,
                    created_at INTEGER DEFAULT (strftime('%s', 'now')),
                    is_deleted INTEGER DEFAULT 0,
                    FOREIGN KEY (chat_id) REFERENCES chats (id) ON DELETE CASCADE
                )
            ''')

            conn.execute('CREATE INDEX IF NOT EXISTS idx_messages_chat_id ON messages(chat_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_messages_deleted ON messages(is_deleted)')

            if conn.execute("SELECT COUNT(*) FROM chats").fetchone()[0] == 0:
                default_chats = [
                    ('0', '⚡️ Urgent', 'urgent'),
                    ('1', '💬 General chat', 'general'),
                    ('2', '🤫 Secrets', 'secrets')
                ]
                conn.executemany("INSERT INTO chats (id, name, seed_suffix) VALUES (?, ?, ?)", default_chats)

            conn.commit()

    def get_config(self) -> Dict[str, str]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM config")
            return {row[0]: row[1] for row in cursor.fetchall()}

    def set_config(self, key: str, value: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT OR REPLACE INTO config VALUES (?, ?)", (key, value))
            conn.commit()

    def get_chats(self) -> Dict[str, Dict]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, seed_suffix FROM chats ORDER BY id")
            return {row[0]: {"name": row[1], "seed_suffix": row[2]} for row in cursor.fetchall()}

    def add_chat(self, chat_id: str, name: str, seed_suffix: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO chats (id, name, seed_suffix) VALUES (?, ?, ?)", (chat_id, name, seed_suffix))
            conn.commit()

    def delete_chat(self, chat_id: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
            conn.commit()

    def save_message(self, msg_type: str, chat_id: str, epoch_index: int, message: str, payload: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO messages (type, chat_id, epoch_index, message, payload, timestamp, datetime)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (msg_type, chat_id, epoch_index, message, payload, epoch_index,
                  datetime.fromtimestamp(epoch_index).isoformat()))
            conn.commit()

    def get_messages(self, chat_id: Optional[str] = None, limit: int = 0, include_deleted: bool = False) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = "SELECT id, type, chat_id, epoch_index, message, payload, timestamp, is_deleted FROM messages"
            params = []

            where_clauses = []
            if not include_deleted:
                where_clauses.append("is_deleted = 0")

            if chat_id:
                where_clauses.append("chat_id = ?")
                params.append(chat_id)

            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)

            query += " ORDER BY timestamp"

            if limit > 0:
                query += " LIMIT ?"
                params.append(limit)

            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_message_count(self, chat_id: Optional[str] = None, include_deleted: bool = False) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            query = "SELECT COUNT(*) FROM messages"
            params = []

            where_clauses = []
            if not include_deleted:
                where_clauses.append("is_deleted = 0")

            if chat_id:
                where_clauses.append("chat_id = ?")
                params.append(chat_id)

            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)

            cursor.execute(query, params)
            return cursor.fetchone()[0]

    def delete_message(self, message_id: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE messages SET is_deleted = 1 WHERE id = ?", (message_id,))
            conn.commit()

    def permanent_delete_message(self, message_id: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM messages WHERE id = ?", (message_id,))
            conn.commit()

    def restore_message(self, message_id: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE messages SET is_deleted = 0 WHERE id = ?", (message_id,))
            conn.commit()

    def clear_chat_history(self, chat_id: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
            conn.commit()
