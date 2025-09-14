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

            # Конфигурация
            conn.execute('''
                CREATE TABLE IF NOT EXISTS config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            ''')

            # Чаты
            conn.execute('''
                CREATE TABLE IF NOT EXISTS chats (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    seed_suffix TEXT NOT NULL
                )
            ''')

            # Сообщения
            conn.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    chat_id TEXT NOT NULL,
                    epoch_index INTEGER NOT NULL,
                    message TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    timestamp INTEGER NOT NULL
                )
            ''')

            # Индексы для скорости
            conn.execute('CREATE INDEX IF NOT EXISTS idx_messages_chat_id ON messages(chat_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)')

            # Чаты по умолчанию
            if conn.execute("SELECT COUNT(*) FROM chats").fetchone()[0] == 0:
                default_chats = [
                    ('0', '⚡️ Urgent', 'urgent'),
                    ('1', '💬 General chat', 'general'),
                    ('2', '🤫 Secrets', 'secrets')
                ]
                conn.executemany("INSERT INTO chats VALUES (?, ?, ?)", default_chats)

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
            conn.execute("INSERT INTO chats VALUES (?, ?, ?)", (chat_id, name, seed_suffix))
            conn.commit()

    def save_message(self, msg_type: str, chat_id: str, epoch_index: int, message: str, payload: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO messages (type, chat_id, epoch_index, message, payload, timestamp, datetime)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (msg_type, chat_id, epoch_index, message, payload, epoch_index,
                  datetime.fromtimestamp(epoch_index).isoformat()))
            conn.commit()

    def get_messages(self, chat_id: Optional[str] = None, limit: int = 0) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = "SELECT type, chat_id, epoch_index, message, payload, timestamp FROM messages"
            params = []

            if chat_id:
                query += " WHERE chat_id = ?"
                params.append(chat_id)

            query += " ORDER BY timestamp"

            if limit > 0:
                query += " LIMIT ?"
                params.append(limit)

            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_message_count(self, chat_id: Optional[str] = None) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if chat_id:
                cursor.execute("SELECT COUNT(*) FROM messages WHERE chat_id = ?", (chat_id,))
            else:
                cursor.execute("SELECT COUNT(*) FROM messages")
            return cursor.fetchone()[0]
