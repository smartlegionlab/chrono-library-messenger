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

    def format_message(self, msg: dict, show_payload: bool = False, show_ids: bool = False) -> str:
        chat_name = self.get_chat_name(msg['chat_id'])
        time_str = datetime.fromtimestamp(msg['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
        direction = "📤" if msg['type'] == 'sent' else "📥"

        status = " 🗑️" if msg.get('is_deleted', 0) == 1 else ""
        message_id = f" [#{msg['id']}]" if show_ids and 'id' in msg else ""

        formatted = f"{direction}{message_id}{status} [{time_str}] {chat_name}:\n{msg['message']}\n"

        if show_payload and msg['type'] == 'sent' and msg.get('is_deleted', 0) == 0:
            formatted += f"   Pointer: {msg['payload']}\n"

        return formatted

    def show_history(self, filter_chat: Optional[str] = None, show_payloads: bool = False,
                     limit: int = 0, show_ids: bool = False, include_deleted: bool = False):
        messages = self.db.get_messages(filter_chat, limit, include_deleted)
        if not messages:
            print("📭 No messages")
            return

        for msg in messages:
            print(self.format_message(msg, show_payloads, show_ids))

        total = self.db.get_message_count(filter_chat, include_deleted)
        active = self.db.get_message_count(filter_chat, False)
        deleted = total - active

        stats = f"\n📊 Showing {len(messages)} of {total} messages"
        if deleted > 0:
            stats += f" ({active} active, {deleted} deleted)"
        print(stats)

    def show_chats(self):
        chats = self.db.get_chats()
        print("💬 Chats:")
        for cid, chat_info in sorted(chats.items(), key=lambda x: int(x[0])):
            message_count = self.db.get_message_count(cid, False)
            total_count = self.db.get_message_count(cid, True)
            deleted_count = total_count - message_count

            stats = f" ({message_count} messages"
            if deleted_count > 0:
                stats += f", {deleted_count} deleted"
            stats += ")"

            print(f"  {cid}: {chat_info['name']}{stats}")
        print(f"📊 Total: {len(chats)} chats")

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

    def delete_chat(self, chat_id: str):
        chat_name = self.get_chat_name(chat_id)
        message_count = self.db.get_message_count(chat_id, True)

        print(f"⚠️  Chat: {chat_id}: {chat_name}")
        print(f"⚠️  Messages: {message_count} total messages")

        confirm = input("❌ Delete this chat and ALL its messages? (y/N): ")
        if confirm.lower() == 'y':
            self.db.delete_chat(chat_id)
            print(f"✅ Chat {chat_id} deleted")
        else:
            print("❌ Deletion cancelled")

    def delete_message(self, message_id: int, permanent: bool = False):
        messages = self.db.get_messages(None, 0, True)
        target_msg = None

        for msg in messages:
            if msg['id'] == message_id:
                target_msg = msg
                break

        if not target_msg:
            print(f"❌ Message #{message_id} not found")
            return

        chat_name = self.get_chat_name(target_msg['chat_id'])
        time_str = datetime.fromtimestamp(target_msg['timestamp']).strftime("%Y-%m-%d %H:%M:%S")

        print(f"⚠️  Message #{message_id}:")
        print(f"   Chat: {target_msg['chat_id']}: {chat_name}")
        print(f"   Time: {time_str}")
        print(f"   Type: {target_msg['type']}")
        print(f"   Content: {target_msg['message'][:50]}...")

        action = "permanently delete" if permanent else "delete"
        confirm = input(f"❌ {action.capitalize()} this message? (y/N): ")

        if confirm.lower() == 'y':
            if permanent:
                self.db.permanent_delete_message(message_id)
                print(f"✅ Message #{message_id} permanently deleted")
            else:
                self.db.delete_message(message_id)
                print(f"✅ Message #{message_id} moved to trash")
        else:
            print("❌ Deletion cancelled")

    def restore_message(self, message_id: int):
        messages = self.db.get_messages(None, 0, True)
        target_msg = None

        for msg in messages:
            if msg['id'] == message_id and msg.get('is_deleted', 0) == 1:
                target_msg = msg
                break

        if not target_msg:
            print(f"❌ Deleted message #{message_id} not found")
            return

        self.db.restore_message(message_id)
        print(f"✅ Message #{message_id} restored")

    def clear_chat_history(self, chat_id: str):
        chat_name = self.get_chat_name(chat_id)
        message_count = self.db.get_message_count(chat_id, True)

        print(f"⚠️  Chat: {chat_id}: {chat_name}")
        print(f"⚠️  Messages: {message_count} total messages")

        confirm = input("❌ PERMANENTLY delete ALL messages in this chat? (y/N): ")
        if confirm.lower() == 'y':
            self.db.clear_chat_history(chat_id)
            print(f"✅ All messages in chat {chat_id} deleted")
        else:
            print("❌ Deletion cancelled")

    def setup_config(self, username: str, master_seed: str):
        if not username.strip() or not master_seed.strip():
            raise ValueError("❌ Username and seed required")
        self.db.set_config('username', username.strip())
        self.db.set_config('master_seed', master_seed.strip())


def main():
    clm = ChronoLibrarian()
    parser = argparse.ArgumentParser(description='Chrono-Library Messenger')
    subparsers = parser.add_subparsers(dest='command', required=True)

    parser_setup = subparsers.add_parser('setup', help='Initial setup')
    parser_setup.add_argument('--username', required=True, help='Your username')
    parser_setup.add_argument('--master-seed', required=True, help='Master seed phrase')

    parser_send = subparsers.add_parser('send', help='Send message')
    parser_send.add_argument('message', help='Message text')
    parser_send.add_argument('--chat', default='1', help='Chat ID')

    parser_recv = subparsers.add_parser('receive', help='Receive message')
    parser_recv.add_argument('payload', help='Pointer JSON')

    parser_history = subparsers.add_parser('history', help='Show history')
    parser_history.add_argument('--chat', help='Filter by chat')
    parser_history.add_argument('--show-pointers', action='store_true', help='Show pointers')
    parser_history.add_argument('--show-ids', action='store_true', help='Show message IDs')
    parser_history.add_argument('--show-deleted', action='store_true', help='Include deleted messages')
    parser_history.add_argument('--limit', type=int, default=0, help='Limit messages')

    subparsers.add_parser('chats', help='List chats')

    parser_add_chat = subparsers.add_parser('add-chat', help='Add new chat')
    parser_add_chat.add_argument('name', help='Chat name')
    parser_add_chat.add_argument('--seed-suffix', help='Seed suffix')

    parser_delete_chat = subparsers.add_parser('delete-chat', help='Delete chat and all messages')
    parser_delete_chat.add_argument('chat_id', help='Chat ID to delete')

    parser_delete_msg = subparsers.add_parser('delete-message', help='Delete message')
    parser_delete_msg.add_argument('message_id', type=int, help='Message ID to delete')
    parser_delete_msg.add_argument('--permanent', action='store_true', help='Permanent deletion')

    parser_restore_msg = subparsers.add_parser('restore-message', help='Restore deleted message')
    parser_restore_msg.add_argument('message_id', type=int, help='Message ID to restore')

    parser_clear = subparsers.add_parser('clear-history', help='Clear chat history')
    parser_clear.add_argument('--chat', required=True, help='Chat ID to clear')

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
            clm.show_history(args.chat, args.show_pointers, args.limit,
                             args.show_ids, args.show_deleted)
        elif args.command == 'chats':
            clm.show_chats()
        elif args.command == 'add-chat':
            clm.add_chat(args.name, args.seed_suffix)
        elif args.command == 'delete-chat':
            clm.delete_chat(args.chat_id)
        elif args.command == 'delete-message':
            clm.delete_message(args.message_id, args.permanent)
        elif args.command == 'restore-message':
            clm.restore_message(args.message_id)
        elif args.command == 'clear-history':
            clm.clear_chat_history(args.chat)
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
