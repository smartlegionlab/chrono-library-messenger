# Copyright © 2025, Alexander Suvorov
import argparse
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple

from .core import HMAC_DRBG, encrypt_decrypt
from .database import CLMDatabase


class ChronoLibrarian:
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "clm"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.db = CLMDatabase(self.config_dir / "clm.db")

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
            raise ValueError("❌ First run: clm setup --username NAME --master-seed SECRET")

        epoch_index = int(time.time())
        signed_message = f"{username}: {message}"

        chat_seed_suffix = self.get_chat_seed_suffix(chat_id)
        seed_material = f"{master_seed}_{chat_seed_suffix}_{epoch_index}".encode()
        drbg = HMAC_DRBG(seed_material)

        message_bytes = signed_message.encode('utf-8')
        key_bytes = drbg.generate(len(message_bytes))
        ciphertext = encrypt_decrypt(message_bytes, key_bytes)

        payload = {'c': chat_id, 'e': epoch_index, 'd': ciphertext.hex()}
        payload_str = json.dumps(payload, ensure_ascii=False)

        self.db.save_message('sent', chat_id, epoch_index, signed_message, payload_str)
        return payload_str

    def receive_message(self, payload_str: str) -> Tuple[Optional[str], Optional[str]]:
        try:
            payload = json.loads(payload_str)
            chat_id = str(payload['c'])
            epoch_index = int(payload['e'])
            ciphertext_hex = payload['d']
        except:
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
            message_bytes = encrypt_decrypt(ciphertext, key_bytes)
            signed_message = message_bytes.decode('utf-8')

            if ": " not in signed_message:
                return None, "❌ Invalid message format"

            self.db.save_message('received', chat_id, epoch_index, signed_message, payload_str)
            return signed_message, None

        except UnicodeDecodeError:
            return None, "❌ Decryption error"

    def format_message(self, msg: dict, show_payload: bool = False) -> str:
        chat_name = self.get_chat_name(msg['chat_id'])
        time_str = datetime.fromtimestamp(msg['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
        direction = "📤" if msg['type'] == 'sent' else "📥"
        formatted = f"{direction} [{time_str}] {chat_name}:\n{msg['message']}\n"
        if show_payload and msg['type'] == 'sent':
            formatted += f"   Pointer: {msg['payload']}\n"
        return formatted

    def show_history(self, filter_chat: Optional[str] = None, show_payloads: bool = False, limit: int = 0):
        messages = self.db.get_messages(filter_chat, limit)
        if not messages:
            print("📭 No messages")
            return
        for msg in messages:
            print(self.format_message(msg, show_payloads))
        total = self.db.get_message_count(filter_chat)
        print(f"\n📊 {len(messages)} of {total} messages")

    def show_chats(self):
        chats = self.db.get_chats()
        print("💬 Chats:")
        for cid, chat_info in sorted(chats.items(), key=lambda x: int(x[0])):
            print(f"  {cid}: {chat_info['name']}")
        print(f"📊 Total: {len(chats)}")

    def add_chat(self, chat_name: str, seed_suffix: Optional[str] = None) -> bool:
        if not chat_name.strip():
            print("❌ Chat name required")
            return False

        chats = self.db.get_chats()
        numeric_ids = [int(k) for k in chats.keys() if k.isdigit()]
        new_id = str(max(numeric_ids) + 1) if numeric_ids else '0'

        if seed_suffix is None:
            seed_suffix = f"chat_{new_id}"

        self.db.add_chat(new_id, chat_name.strip(), seed_suffix)
        print(f"✅ Chat added: {new_id}: {chat_name}")
        return True

    def setup_config(self, username: str, master_seed: str):
        if not username.strip() or not master_seed.strip():
            raise ValueError("❌ Username and seed required")
        self.db.set_config('username', username.strip())
        self.db.set_config('master_seed', master_seed.strip())


def main():
    clm = ChronoLibrarian()
    parser = argparse.ArgumentParser(description='Chrono-Library Messenger')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Setup
    parser_setup = subparsers.add_parser('setup', help='Initial setup')
    parser_setup.add_argument('--username', required=True, help='Your username')
    parser_setup.add_argument('--master-seed', required=True, help='Master seed phrase')

    # Send
    parser_send = subparsers.add_parser('send', help='Send message')
    parser_send.add_argument('message', help='Message text')
    parser_send.add_argument('--chat', default='1', help='Chat ID')

    # Receive
    parser_recv = subparsers.add_parser('receive', help='Receive message')
    parser_recv.add_argument('payload', help='Pointer JSON')

    # History
    parser_history = subparsers.add_parser('history', help='Show history')
    parser_history.add_argument('--chat', help='Filter by chat')
    parser_history.add_argument('--show-pointers', action='store_true', help='Show pointers')
    parser_history.add_argument('--limit', type=int, default=0, help='Limit messages')

    # Chats
    subparsers.add_parser('chats', help='List chats')

    # Add chat
    parser_add_chat = subparsers.add_parser('add-chat', help='Add new chat')
    parser_add_chat.add_argument('name', help='Chat name')
    parser_add_chat.add_argument('--seed-suffix', help='Seed suffix')

    args = parser.parse_args()

    try:
        if args.command == 'setup':
            clm.setup_config(args.username, args.master_seed)
            print("✅ Configuration saved")
            clm.show_chats()
        elif args.command == 'send':
            payload = clm.send_message(args.message, args.chat)
            print("✅ Message sent")
            print(f"📤 Pointer:\n{payload}")
        elif args.command == 'receive':
            message, error = clm.receive_message(args.payload)
            print(error if error else f"✅ Message:\n{message}")
        elif args.command == 'history':
            clm.show_history(args.chat, args.show_pointers, args.limit)
        elif args.command == 'chats':
            clm.show_chats()
        elif args.command == 'add-chat':
            clm.add_chat(args.name, args.seed_suffix)
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
