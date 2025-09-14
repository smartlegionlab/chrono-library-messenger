# Copyright © 2025, Alexander Suvorov
# Chrono-Library Messenger (CLM)
import argparse
import hmac
import hashlib
import time
import json
from datetime import datetime
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "clm"
CONFIG_FILE = CONFIG_DIR / "config.json"
CHATS_FILE = CONFIG_DIR / "chats.json"
SENT_DIR = CONFIG_DIR / "sent"
RECEIVED_DIR = CONFIG_DIR / "received"

DEFAULT_CHATS = {
    "0": {"name": "⚡️ Urgent", "seed_suffix": "urgent"},
    "1": {"name": "💬 General chat", "seed_suffix": "general"},
    "2": {"name": "🤫 Secrets", "seed_suffix": "secrets"}
}


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


def ensure_config():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    SENT_DIR.mkdir(exist_ok=True)
    RECEIVED_DIR.mkdir(exist_ok=True)

    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'w') as f:
            json.dump({"username": "", "master_seed": ""}, f)

    if not CHATS_FILE.exists():
        with open(CHATS_FILE, 'w') as f:
            json.dump(DEFAULT_CHATS, f, ensure_ascii=False, indent=2)


def get_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)


def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def get_chats():
    with open(CHATS_FILE, 'r') as f:
        return json.load(f)


def get_chat_name(chat_id):
    chats = get_chats()
    if chat_id in chats:
        return chats[chat_id]["name"]
    return f"Чат {chat_id}"


def get_chat_seed_suffix(chat_id):
    chats = get_chats()
    if chat_id in chats:
        return chats[chat_id]["seed_suffix"]
    return f"chat_{chat_id}"


def save_sent_message(chat_id, epoch_index, message, payload):
    filename = SENT_DIR / f"{epoch_index}_{chat_id}.json"

    data = {
        'type': 'sent',
        'chat_id': chat_id,
        'epoch_index': epoch_index,
        'timestamp': epoch_index,
        'message': message,
        'payload': payload,
        'datetime': datetime.fromtimestamp(epoch_index).isoformat()
    }

    with open(filename, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_received_message(chat_id, epoch_index, message, payload):
    filename = RECEIVED_DIR / f"{epoch_index}_{chat_id}.json"

    data = {
        'type': 'received',
        'chat_id': chat_id,
        'epoch_index': epoch_index,
        'timestamp': epoch_index,
        'message': message,
        'payload': payload,
        'datetime': datetime.fromtimestamp(epoch_index).isoformat()
    }

    with open(filename, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_message_history():
    history = []

    for file in SENT_DIR.glob("*.json"):
        with open(file, 'r') as f:
            history.append(json.load(f))

    for file in RECEIVED_DIR.glob("*.json"):
        with open(file, 'r') as f:
            history.append(json.load(f))

    return sorted(history, key=lambda x: x['timestamp'])


def encrypt_decrypt(data, key):
    return bytes([d ^ k for d, k in zip(data, key)])


def send_message(message, chat_id):
    config = get_config()
    master_seed = config['master_seed']
    username = config['username']

    epoch_index = int(time.time())

    signed_message = f"{username}: {message}"

    chat_seed_suffix = get_chat_seed_suffix(chat_id)
    seed_material = f"{master_seed}_{chat_seed_suffix}_{epoch_index}".encode()
    drbg = HMAC_DRBG(seed_material)

    message_bytes = signed_message.encode('utf-8')
    key_bytes = drbg.generate(len(message_bytes))
    ciphertext = encrypt_decrypt(message_bytes, key_bytes)

    payload = {
        'c': chat_id,
        'e': epoch_index,
        'd': ciphertext.hex()
    }

    payload_str = json.dumps(payload, ensure_ascii=False)

    save_sent_message(chat_id, epoch_index, signed_message, payload_str)

    return payload_str


def receive_message(payload_str):
    try:
        payload = json.loads(payload_str)
        chat_id = str(payload['c'])
        epoch_index = int(payload['e'])
        ciphertext_hex = payload['d']
    except (json.JSONDecodeError, KeyError):
        return None, "❌ Invalid pointer format"

    config = get_config()
    master_seed = config['master_seed']

    chat_seed_suffix = get_chat_seed_suffix(chat_id)
    seed_material = f"{master_seed}_{chat_seed_suffix}_{epoch_index}".encode()
    drbg = HMAC_DRBG(seed_material)

    ciphertext = bytes.fromhex(ciphertext_hex)
    key_bytes = drbg.generate(len(ciphertext))

    try:
        message_bytes = encrypt_decrypt(ciphertext, key_bytes)
        signed_message = message_bytes.decode('utf-8')

        save_received_message(chat_id, epoch_index, signed_message, payload_str)

        return signed_message, None
    except UnicodeDecodeError:
        return None, "❌ Decryption error. Possibly invalid chat or seed phrase.."


def format_message(msg, show_payload=False):
    chat_name = get_chat_name(msg['chat_id'])
    dt = datetime.fromtimestamp(msg['timestamp'])
    time_str = dt.strftime("%Y-%m-%d %H:%M:%S")

    direction = "📤" if msg['type'] == 'sent' else "📥"
    formatted_msg = f"{direction} [{time_str}] {chat_name}:\n{msg['message']}\n"

    if show_payload and msg['type'] == 'sent':
        formatted_msg += f"   Pointer: {msg['payload']}\n"

    return formatted_msg


def show_history(filter_chat=None, show_payloads=False):
    history = get_message_history()

    if not history:
        print("📭 Message history is empty")
        return

    print()
    for msg in history:
        if filter_chat and msg['chat_id'] != filter_chat:
            continue

        print(format_message(msg, show_payloads))


def show_chats():
    chats = get_chats()
    print("💬 Available chats:")
    for cid, chat_info in chats.items():
        print(f"  {cid}: {chat_info['name']}")


def add_chat(chat_name, seed_suffix=None):
    chats = get_chats()
    new_id = str(max([int(k) for k in chats.keys()] + [0]) + 1)

    if seed_suffix is None:
        seed_suffix = f"chat_{new_id}"

    chats[new_id] = {
        "name": chat_name,
        "seed_suffix": seed_suffix
    }

    with open(CHATS_FILE, 'w') as f:
        json.dump(chats, f, ensure_ascii=False, indent=2)

    print(f"✅ New chat added: {new_id}: {chat_name}")


def main():
    ensure_config()

    parser = argparse.ArgumentParser(description='Chrono-Library Messenger - Messenger without data transfer',
                                     formatter_class=argparse.RawTextHelpFormatter)
    subparsers = parser.add_subparsers(dest='command', required=True)

    parser_setup = subparsers.add_parser('setup', help='Initial setup')
    parser_setup.add_argument('--username', type=str, required=True, help='Your login (for example, @sid)')
    parser_setup.add_argument('--master-seed', type=str, required=True, help='Main seed phrase')

    parser_send = subparsers.add_parser('send', help='Send message')
    parser_send.add_argument('message', type=str, help='Message text')
    parser_send.add_argument('--chat', type=str, default='1', help='Chat ID')

    parser_recv = subparsers.add_parser('receive', help='Get message')
    parser_recv.add_argument('payload', type=str, help='Public index in JSON format')

    parser_history = subparsers.add_parser('history', help='Show chat history')
    parser_history.add_argument('--chat', type=str, help='Filter by chat')
    parser_history.add_argument('--show-pointers', action='store_true', help='Show public signs')

    parser_chats = subparsers.add_parser('chats', help='Show chat list')

    parser_add_chat = subparsers.add_parser('add-chat', help='Add new chat')
    parser_add_chat.add_argument('name', type=str, help='Chat name')
    parser_add_chat.add_argument('--seed-suffix', type=str, help='Unique suffix for seed (optional)')

    args = parser.parse_args()

    if args.command == 'setup':
        config = {
            'username': args.username,
            'master_seed': args.master_seed

        }
        save_config(config)
        print("✅ Configuration saved!")
        print(f"👤 Your login: {args.username}")
        show_chats()

    elif args.command == 'send':
        config = get_config()
        if not config['master_seed']:
            print("❌ First, do the setup: clm setup --username YourLogin --master-seed YourPhrase")
            return

        payload = send_message(args.message, args.chat)
        print("✅ The message has been saved in history!")
        print("\n📤 Public pointer (for transfer):")
        print(payload)

    elif args.command == 'receive':
        config = get_config()
        if not config['master_seed']:
            print("❌ First, do the setup: clm setup --username YourLogin --master-seed YourPhrase")
            return

        message, error = receive_message(args.payload)
        if error:
            print(error)
        else:
            print("✅ Message received!")
            print(f"\n{message}")

    elif args.command == 'history':
        show_history(args.chat, args.show_pointers)

    elif args.command == 'chats':
        show_chats()

    elif args.command == 'add-chat':
        add_chat(args.name, args.seed_suffix)


if __name__ == "__main__":
    main()
