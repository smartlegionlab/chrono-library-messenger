# Copyright © 2025, Alexander Suvorov
import argparse
import hmac
import hashlib
import time
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class HMAC_DRBG:
    def __init__(self, seed_material):
        self.K = b'\x00' * 32
        self.V = b'\x01' * 32
        self._update(seed_material)

    def _update(self, provided_data=None):
        data = provided_data if provided_data else b''
        self.K = hmac.new(self.K, self.V + b'\x00' + data, hashlib.sha256).digest()
        self.V = hmac.new(self.K, self.V, hashlib.sha256).digest()
        if provided_data:
            self.K = hmac.new(self.K, self.V + b'\x01' + data, hashlib.sha256).digest()
            self.V = hmac.new(self.K, self.V, hashlib.sha256).digest()

    def generate(self, num_bytes):
        temp = b''
        while len(temp) < num_bytes:
            self.V = hmac.new(self.K, self.V, hashlib.sha256).digest()
            temp += self.V
        return temp[:num_bytes]


class CLMDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")

            # Config table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            ''')

            # Chats table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS chats (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    seed_suffix TEXT NOT NULL,
                    created_at INTEGER DEFAULT (strftime('%s', 'now'))
                )
            ''')

            # Messages table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL CHECK (type IN ('sent', 'received')),
                    chat_id TEXT NOT NULL,
                    epoch_index INTEGER NOT NULL,
                    message TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    timestamp INTEGER NOT NULL,
                    datetime TEXT NOT NULL,
                    created_at INTEGER DEFAULT (strftime('%s', 'now')),
                    FOREIGN KEY (chat_id) REFERENCES chats (id) ON DELETE CASCADE
                )
            ''')

            # Indexes for performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_messages_chat_id ON messages(chat_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_messages_epoch_index ON messages(epoch_index)')

            # Insert default chats if none exist
            if conn.execute("SELECT COUNT(*) FROM chats").fetchone()[0] == 0:
                default_chats = [
                    ('0', '⚡️ Urgent', 'urgent'),
                    ('1', '💬 General chat', 'general'),
                    ('2', '🤫 Secrets', 'secrets')
                ]
                conn.executemany(
                    "INSERT INTO chats (id, name, seed_suffix) VALUES (?, ?, ?)",
                    default_chats
                )

            conn.commit()

    def get_config(self) -> Dict[str, str]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM config")
            return {row[0]: row[1] for row in cursor.fetchall()}

    def set_config(self, key: str, value: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                (key, value)
            )
            conn.commit()

    def get_chats(self) -> Dict[str, Dict]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, seed_suffix FROM chats ORDER BY id")
            return {row[0]: {"name": row[1], "seed_suffix": row[2]} for row in cursor.fetchall()}

    def add_chat(self, chat_id: str, name: str, seed_suffix: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO chats (id, name, seed_suffix) VALUES (?, ?, ?)",
                (chat_id, name, seed_suffix)
            )
            conn.commit()

    def save_message(self, msg_type: str, chat_id: str, epoch_index: int,
                     message: str, payload: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                '''INSERT INTO messages 
                (type, chat_id, epoch_index, message, payload, timestamp, datetime)
                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (msg_type, chat_id, epoch_index, message, payload,
                 epoch_index, datetime.fromtimestamp(epoch_index).isoformat())
            )
            conn.commit()

    def get_messages(self, chat_id: Optional[str] = None, limit: int = 0,
                     offset: int = 0) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = '''
                SELECT type, chat_id, epoch_index, message, payload, timestamp, datetime
                FROM messages
            '''
            params = []

            if chat_id:
                query += " WHERE chat_id = ?"
                params.append(chat_id)

            query += " ORDER BY timestamp"

            if limit > 0:
                query += " LIMIT ?"
                params.append(limit)
                if offset > 0:
                    query += " OFFSET ?"
                    params.append(offset)

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

    def export_data(self, export_path: Path):
        import shutil
        shutil.copy2(self.db_path, export_path)

    def import_data(self, import_path: Path):
        import shutil
        shutil.copy2(import_path, self.db_path)


class ChronoLibrarian:
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "clm"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.db = CLMDatabase(self.config_dir / "clm.db")

    def encrypt_decrypt(self, data, key):
        return bytes([d ^ k for d, k in zip(data, key)])

    def get_chat_name(self, chat_id: str) -> str:
        chats = self.db.get_chats()
        return chats.get(chat_id, {}).get("name", f"Chat {chat_id}")

    def get_chat_seed_suffix(self, chat_id: str) -> str:
        chats = self.db.get_chats()
        return chats.get(chat_id, {}).get("seed_suffix", f"chat_{chat_id}")

    def send_message(self, message: str, chat_id: str) -> str:
        config = self.db.get_config()
        master_seed = config.get('master_seed', '')
        username = config.get('username', '')

        if not master_seed or not username:
            raise ValueError("Configuration not complete. Please run setup first.")

        epoch_index = int(time.time())
        signed_message = f"{username}: {message}"

        chat_seed_suffix = self.get_chat_seed_suffix(chat_id)
        seed_material = f"{master_seed}_{chat_seed_suffix}_{epoch_index}".encode()
        drbg = HMAC_DRBG(seed_material)

        message_bytes = signed_message.encode('utf-8')
        key_bytes = drbg.generate(len(message_bytes))
        ciphertext = self.encrypt_decrypt(message_bytes, key_bytes)

        payload = {
            'c': chat_id,
            'e': epoch_index,
            'd': ciphertext.hex()
        }

        payload_str = json.dumps(payload, ensure_ascii=False)
        self.db.save_message('sent', chat_id, epoch_index, signed_message, payload_str)

        return payload_str

    def receive_message(self, payload_str: str) -> Tuple[Optional[str], Optional[str]]:
        try:
            payload = json.loads(payload_str)
            chat_id = str(payload['c'])
            epoch_index = int(payload['e'])
            ciphertext_hex = payload['d']
        except (json.JSONDecodeError, KeyError, ValueError):
            return None, "❌ Invalid pointer format"

        config = self.db.get_config()
        master_seed = config.get('master_seed', '')

        if not master_seed:
            return None, "❌ Master seed not configured"

        chat_seed_suffix = self.get_chat_seed_suffix(chat_id)
        seed_material = f"{master_seed}_{chat_seed_suffix}_{epoch_index}".encode()
        drbg = HMAC_DRBG(seed_material)

        ciphertext = bytes.fromhex(ciphertext_hex)
        key_bytes = drbg.generate(len(ciphertext))

        try:
            message_bytes = self.encrypt_decrypt(ciphertext, key_bytes)
            signed_message = message_bytes.decode('utf-8')

            if ": " not in signed_message:
                return None, "❌ Decryption successful but the message format is invalid. Likely wrong chat or seed."

            self.db.save_message('received', chat_id, epoch_index, signed_message, payload_str)
            return signed_message, None

        except UnicodeDecodeError:
            return None, "❌ Decryption error. Possible reasons: invalid master seed, wrong chat, or corrupted pointer."

    def format_message(self, msg: Dict, show_payload: bool = False) -> str:
        chat_name = self.get_chat_name(msg['chat_id'])
        dt = datetime.fromtimestamp(msg['timestamp'])
        time_str = dt.strftime("%Y-%m-%d %H:%M:%S")

        direction = "📤" if msg['type'] == 'sent' else "📥"
        formatted_msg = f"{direction} [{time_str}] {chat_name}:\n{msg['message']}\n"

        if show_payload and msg['type'] == 'sent':
            formatted_msg += f"   Pointer: {msg['payload']}\n"

        return formatted_msg

    def show_history(self, filter_chat: Optional[str] = None,
                     show_payloads: bool = False, limit: int = 0):
        messages = self.db.get_messages(filter_chat, limit)

        if not messages:
            print("📭 Message history is empty")
            return

        print()
        for msg in messages:
            print(self.format_message(msg, show_payloads))

        total_count = self.db.get_message_count(filter_chat)
        print(f"\n📊 Showing {len(messages)} of {total_count} total messages")

    def show_chats(self):
        chats = self.db.get_chats()
        print("💬 Available chats:")
        for cid, chat_info in sorted(chats.items(), key=lambda x: int(x[0])):
            print(f"  {cid}: {chat_info['name']}")
        print(f"\n📊 Total chats: {len(chats)}")

    def add_chat(self, chat_name: str, seed_suffix: Optional[str] = None) -> bool:
        if not chat_name.strip():
            print("❌ Chat name cannot be empty")
            return False

        chats = self.db.get_chats()
        numeric_ids = [int(k) for k in chats.keys() if k.isdigit()]
        new_id = str(max(numeric_ids) + 1) if numeric_ids else '0'

        if seed_suffix is None:
            seed_suffix = f"chat_{new_id}"

        self.db.add_chat(new_id, chat_name.strip(), seed_suffix)
        print(f"✅ New chat added: {new_id}: {chat_name}")
        return True

    def setup_config(self, username: str, master_seed: str):
        if not username.strip():
            raise ValueError("Username cannot be empty")
        if not master_seed.strip():
            raise ValueError("Master seed cannot be empty")

        self.db.set_config('username', username.strip())
        self.db.set_config('master_seed', master_seed.strip())

    def export_profile(self, path: str):
        try:
            export_path = Path(path) / "clm_backup.db"
            self.db.export_data(export_path)
            print(f"✅ Profile exported to: {export_path}")
            return True
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return False

    def import_profile(self, path: str):
        try:
            import_path = Path(path)
            if not import_path.exists():
                print("❌ Import path does not exist")
                return False

            backup_path = self.config_dir / "clm_backup_old.db"
            if self.db.db_path.exists():
                import shutil
                shutil.copy2(self.db.db_path, backup_path)

            self.db.import_data(import_path)
            print(f"✅ Profile imported from: {import_path}")
            if backup_path.exists():
                print(f"📦 Old profile backed up to: {backup_path}")
            return True
        except Exception as e:
            print(f"❌ Import failed: {e}")
            return False


def main():
    clm = ChronoLibrarian()

    parser = argparse.ArgumentParser(
        description='Chrono-Library Messenger - Messenger without data transfer',
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Setup command
    parser_setup = subparsers.add_parser('setup', help='Initial setup')
    parser_setup.add_argument('--username', type=str, required=True,
                              help='Your login (for example, @sid)')
    parser_setup.add_argument('--master-seed', type=str, required=True,
                              help='Main seed phrase')

    # Send command
    parser_send = subparsers.add_parser('send', help='Send message')
    parser_send.add_argument('message', type=str, help='Message text')
    parser_send.add_argument('--chat', type=str, default='1', help='Chat ID')

    # Receive command
    parser_recv = subparsers.add_parser('receive', help='Get message')
    parser_recv.add_argument('payload', type=str, help='Public pointer in JSON format')

    # History command
    parser_history = subparsers.add_parser('history', help='Show chat history')
    parser_history.add_argument('--chat', type=str, help='Filter by chat ID')
    parser_history.add_argument('--show-pointers', action='store_true',
                                help='Show public pointers')
    parser_history.add_argument('--limit', type=int, default=0,
                                help='Limit number of messages to show')

    # Chats command
    subparsers.add_parser('chats', help='Show chat list')

    # Add-chat command
    parser_add_chat = subparsers.add_parser('add-chat', help='Add new chat')
    parser_add_chat.add_argument('name', type=str, help='Chat name')
    parser_add_chat.add_argument('--seed-suffix', type=str,
                                 help='Unique suffix for seed (optional)')

    # Export command
    parser_export = subparsers.add_parser('export', help='Export profile backup')
    parser_export.add_argument('path', type=str, help='Path to export backup')

    # Import command
    parser_import = subparsers.add_parser('import', help='Import profile backup')
    parser_import.add_argument('path', type=str, help='Path to import backup from')

    args = parser.parse_args()

    try:
        if args.command == 'setup':
            clm.setup_config(args.username, args.master_seed)
            print("✅ Configuration saved!")
            print(f"👤 Your login: {args.username}")
            clm.show_chats()

        elif args.command == 'send':
            payload = clm.send_message(args.message, args.chat)
            print("✅ The message has been saved in history!")
            print("\n📤 Public pointer (for transfer):")
            print(payload)

        elif args.command == 'receive':
            message, error = clm.receive_message(args.payload)
            if error:
                print(error)
            else:
                print("✅ Message received!")
                print(f"\n{message}")

        elif args.command == 'history':
            clm.show_history(args.chat, args.show_pointers, args.limit)

        elif args.command == 'chats':
            clm.show_chats()

        elif args.command == 'add-chat':
            clm.add_chat(args.name, args.seed_suffix)

        elif args.command == 'export':
            clm.export_profile(args.path)

        elif args.command == 'import':
            if input("❓ This will overwrite your current profile. Continue? (y/N): ").lower() == 'y':
                clm.import_profile(args.path)
            else:
                print("❌ Import cancelled")

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
