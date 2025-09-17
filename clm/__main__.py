# Copyright © 2025, Alexander Suvorov
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple
import sys

from .core import HMAC_DRBG, encrypt_decrypt
from .database import CLMDatabase
from .auth import AuthManager


class ChronoLibrarianCLI:
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "clm"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.db = CLMDatabase(self.config_dir / "clm.db")
        self.auth = AuthManager(self.db)
        self.current_chat = None
        self.master_seed = None
        self.username = None

    def safe_input(self, prompt):
        try:
            return input(prompt).strip()
        except UnicodeDecodeError:
            try:
                user_input = input(prompt)
                return user_input.encode('latin-1').decode('utf-8').strip()
            except:
                return input(prompt).encode('utf-8', errors='ignore').decode('utf-8').strip()

    def setup(self):
        print("🔄 Setting up Chrono-Library Messenger")
        print("=" * 50)

        username = self.safe_input("Enter your nickname: ")
        if not username:
            print("❌ Nickname is required")
            return False

        master_seed = self.safe_input("Enter your secret phrase: ")
        if not master_seed:
            print("❌ Secret phrase is required")
            return False

        confirm = self.safe_input("Repeat the secret phrase: ")
        if master_seed != confirm:
            print("❌ The phrases do not match")
            return False

        try:
            public_key = self.auth.generate_public_key(username, master_seed)
            self.db.set_config('username', username)
            self.db.set_config('public_key', public_key)

            print("✅ Setup complete!")
            print(f"👤 Your nickname: {username}")
            print("🔑 The public key has been saved.")
            return True
        except Exception as e:
            print(f"❌ Configuration error: {e}")
            return False

    def login(self):
        print("🔐 Login to Chrono-Library Messenger")
        print("=" * 50)

        config = self.db.get_config()
        if 'public_key' not in config:
            print("❌ Initial setup required")
            return False

        self.username = config.get('username', '')
        stored_public_key = config.get('public_key', '')

        master_seed = self.safe_input("Enter your secret phrase: ")
        if not master_seed:
            print("❌ Secret phrase is required")
            return False

        if self.auth.verify_secret(self.username, master_seed, stored_public_key):
            self.master_seed = master_seed
            print("✅ Successful login!")
            return True
        else:
            print("❌ Invalid secret phrase")
            return False

    def show_main_menu(self):
        while True:
            print("\n" + "=" * 50)
            print("🌌 CHRONO-LIBRARY MESSENGER")
            print("=" * 50)
            print(f"👤 User: {self.username}")
            print("1. 💬 My chats")
            print("2. ➕ Create a new chat")
            print("3. 📨 Send message")
            print("4. 📩 Receive a message")
            print("5. 📜 Message history")
            print("6. ⚙️ Profile settings")
            print("7. 🚪 Exit")

            choice = self.safe_input("\nSelect an action (1-7): ")

            if choice == '1':
                self.show_chats_menu()
            elif choice == '2':
                self.create_chat()
            elif choice == '3':
                self.send_message_menu()
            elif choice == '4':
                self.receive_message_menu()
            elif choice == '5':
                self.show_history_menu()
            elif choice == '6':
                self.settings_menu()
            elif choice == '7':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Wrong choice")

    def delete_message_menu(self):
        try:
            msg_id = int(self.safe_input("Enter message ID to delete: "))

            messages = self.db.get_messages(None, 0, True)  # include_deleted=True
            found = None

            for msg in messages:
                if msg['id'] == msg_id:
                    found = msg
                    break

            if not found:
                print("❌ Message not found")
                return

            chat_name = self.get_chat_name(found['chat_id'])
            time_str = datetime.fromtimestamp(found['timestamp']).strftime("%Y-%m-%d %H:%M:%S")

            print(f"\n🗑️ Delete message #{msg_id}:")
            print(f"   Chat: {chat_name}")
            print(f"   Time: {time_str}")
            print(f"   Type: {found['type']}")
            print(f"   Content: {found['message'][:50]}...")

            confirm = self.safe_input("❌ Move this message to trash? (y/N): ").lower()
            if confirm == 'y':
                self.db.delete_message(msg_id)
                print("✅ Message moved to trash")
            else:
                print("❌ Deletion cancelled")

        except ValueError:
            print("❌ Enter a valid number")

    def show_chats_menu(self):
        while True:
            chats = self.db.get_chats()
            if not chats:
                print("📭 There are no chats")
                return

            print("\n" + "=" * 50)
            print("💬 MY CHATS")
            print("=" * 50)

            for i, (cid, chat_info) in enumerate(sorted(chats.items(), key=lambda x: int(x[0])), 1):
                msg_count = self.db.get_message_count(cid, False)
                print(f"{i}. {chat_info['name']} ({msg_count} message.)")

            print(f"{len(chats) + 1}. ↩️ Back")

            try:
                choice = int(self.safe_input(f"\nSelect a chat (1-{len(chats) + 1}): "))
                if 1 <= choice <= len(chats):
                    chat_id = list(sorted(chats.keys(), key=int))[choice - 1]
                    self.chat_details_menu(chat_id)
                elif choice == len(chats) + 1:
                    break
                else:
                    print("❌ Wrong choice")
            except ValueError:
                print("❌ Enter the number")

    def chat_details_menu(self, chat_id):
        chat_name = self.get_chat_name(chat_id)

        while True:
            print(f"\n💬 CHAT: {chat_name}")
            print("1. 📨 Send message")
            print("2. 📜 View history")
            print("3. 🗑️ Clear history")
            print("4. ❌ Delete chat")
            print("5. ↩️ Back")

            choice = self.safe_input("\nSelect an action (1-5): ")

            if choice == '1':
                self.send_message_to_chat(chat_id)
            elif choice == '2':
                self.show_chat_history(chat_id)
            elif choice == '3':
                self.clear_chat_history(chat_id)
            elif choice == '4':
                self.delete_chat(chat_id)
                break
            elif choice == '5':
                break
            else:
                print("❌ Wrong choice")

    def show_chat_history(self, chat_id):
        messages = self.db.get_messages(chat_id, 0, False)
        if not messages:
            print("📭 No messages")
            return

        self.display_messages(messages, True)

    def clear_chat_history(self, chat_id):
        chat_name = self.get_chat_name(chat_id)
        message_count = self.db.get_message_count(chat_id, True)

        print(f"⚠️  Chat: {chat_id}: {chat_name}")
        print(f"⚠️  Messages: {message_count} total")

        confirm = self.safe_input("❌ DELETE ALL messages in this chat? (y/N): ").lower()
        if confirm == 'y':
            self.db.clear_chat_history(chat_id)
            print(f"✅ All messages in the chat {chat_id} removed")
        else:
            print("❌ Deletion cancelled")

    def delete_chat(self, chat_id):
        chat_name = self.get_chat_name(chat_id)
        message_count = self.db.get_message_count(chat_id, True)

        print(f"⚠️  Chat: {chat_id}: {chat_name}")
        print(f"⚠️  Messages: {message_count} total")

        confirm = self.safe_input("❌ Delete this chat and ALL its messages? (y/N): ").lower()
        if confirm == 'y':
            self.db.delete_chat(chat_id)
            print(f"✅ Chat {chat_id} has been deleted")
        else:
            print("❌ Deletion cancelled")

    def send_message_menu(self):
        chats = self.db.get_chats()
        if not chats:
            print("❌ First, create a chat")
            return

        print("\n📨 SENDING A MESSAGE")
        print("=" * 50)

        for i, (cid, chat_info) in enumerate(sorted(chats.items(), key=lambda x: int(x[0])), 1):
            print(f"{i}. {chat_info['name']}")

        print(f"{len(chats) + 1}. ↩️ Back")

        try:
            choice = int(self.safe_input(f"\nSelect a chat (1-{len(chats) + 1}): "))
            if 1 <= choice <= len(chats):
                chat_id = list(sorted(chats.keys(), key=int))[choice - 1]
                self.send_message_to_chat(chat_id)
            elif choice != len(chats) + 1:
                print("❌ Wrong choice")
        except ValueError:
            print("❌ Enter the number")

    def send_message_to_chat(self, chat_id):
        chat_name = self.get_chat_name(chat_id)
        print(f"\n📨 Sending to: {chat_name}")

        message = self.safe_input("Enter your message: ")
        if not message:
            print("❌ The message cannot be empty")
            return

        try:
            payload = self.send_message(message, chat_id)
            print("✅ Message sent!")
            print("\n📋 Pointer for:")
            print(payload)
            input("\nPress Enter to continue...")
        except Exception as e:
            print(f"❌ Sending error: {e}")

    def receive_message_menu(self):
        print("\n📩 RECEIVING A MESSAGE")
        print("=" * 50)
        print("Enter the message index (JSON):")
        print("Or enter 'back' to return")

        payload_str = self.safe_input("")
        if payload_str.lower() == 'back':
            return

        try:
            message, error = self.receive_message(payload_str)
            if error:
                print(f"❌ {error}")
            else:
                print(f"\n✅ Message received:")
                print(message)
                input("\nPress Enter to continue...")
        except Exception as e:
            print(f"❌ Error: {e}")

    def show_history_menu(self):
        while True:
            print("\n📜 MESSAGE HISTORY")
            print("=" * 50)
            print("1. 📋 All messages")
            print("2. 💬 By chats")
            print("3. 🔍 Search by ID")
            print("4. 🗑️ Basket")
            print("5. ❌ Delete message")
            print("6. ↩️ Back")

            choice = self.safe_input("\nSelect an action (1-6): ")

            if choice == '1':
                self.show_all_history()
            elif choice == '2':
                self.show_history_by_chat()
            elif choice == '3':
                self.search_by_id()
            elif choice == '4':
                self.trash_menu()
            elif choice == '5':
                self.delete_message_menu()
            elif choice == '6':
                break
            else:
                print("❌ Wrong choice")

    def show_all_history(self):
        messages = self.db.get_messages(None, 0, False)
        if not messages:
            print("📭 No messages")
            return

        self.display_messages(messages, True)

    def show_history_by_chat(self):
        chats = self.db.get_chats()
        if not chats:
            print("❌ There are no chats")
            return

        for i, (cid, chat_info) in enumerate(sorted(chats.items(), key=lambda x: int(x[0])), 1):
            msg_count = self.db.get_message_count(cid, False)
            print(f"{i}. {chat_info['name']} ({msg_count} message.)")

        print(f"{len(chats) + 1}. ↩️ Back")

        try:
            choice = int(self.safe_input(f"\nSelect a chat (1-{len(chats) + 1}): "))
            if 1 <= choice <= len(chats):
                chat_id = list(sorted(chats.keys(), key=int))[choice - 1]
                messages = self.db.get_messages(chat_id, 0, False)
                self.display_messages(messages, True)
            elif choice != len(chats) + 1:
                print("❌ Wrong choice")
        except ValueError:
            print("❌ Enter the number")

    def search_by_id(self):
        try:
            msg_id = int(self.safe_input("Введите ID сообщения: "))
            messages = self.db.get_messages(None, 0, True)
            found = None

            for msg in messages:
                if msg['id'] == msg_id:
                    found = msg
                    break

            if found:
                self.display_message_detail(found)
            else:
                print("❌ Message not found")
        except ValueError:
            print("❌ Enter the number")

    def trash_menu(self):
        while True:
            deleted_msgs = [msg for msg in self.db.get_messages(None, 0, True)
                            if msg.get('is_deleted', 0) == 1]

            if not deleted_msgs:
                print("🗑️ The cart is empty")
                return

            print(f"\n🗑️ BASKET ({len(deleted_msgs)} message.)")
            print("=" * 50)

            for i, msg in enumerate(deleted_msgs, 1):
                chat_name = self.get_chat_name(msg['chat_id'])
                time_str = datetime.fromtimestamp(msg['timestamp']).strftime("%Y-%m-%d %H:%M")
                preview = msg['message'][:30] + "..." if len(msg['message']) > 30 else msg['message']
                print(f"{i}. [{time_str}] {chat_name}: {preview}")

            print(f"{len(deleted_msgs) + 1}. ↩️ Back")

            try:
                choice = int(self.safe_input(f"\nSelect a message (1-{len(deleted_msgs) + 1}): "))
                if 1 <= choice <= len(deleted_msgs):
                    if self.manage_deleted_message(deleted_msgs[choice - 1]):
                        break
                elif choice == len(deleted_msgs) + 1:
                    break
                else:
                    print("❌ Wrong choice")
            except ValueError:
                print("❌ Enter the number")

    def manage_deleted_message(self, msg):
        chat_name = self.get_chat_name(msg['chat_id'])
        time_str = datetime.fromtimestamp(msg['timestamp']).strftime("%Y-%m-%d %H:%M:%S")

        print(f"\n🗑️ Message #{msg['id']}:")
        print(f"   Chat: {chat_name}")
        print(f"   Time: {time_str}")
        print(f"   Type: {msg['type']}")
        print(f"   Content: {msg['message']}")

        print("\n1. 🔄 Restore")
        print("2. 🗑️ Delete permanently")
        print("3. ↩️ Back")

        choice = self.safe_input("\nSelect an action (1-3): ")

        if choice == '1':
            self.db.restore_message(msg['id'])
            print("✅ The message has been restored.")
            return True
        elif choice == '2':
            confirm = self.safe_input("❌ Delete permanently? (y/N): ").lower()
            if confirm == 'y':
                self.db.permanent_delete_message(msg['id'])
                print("✅ The message has been permanently deleted.")
                return True
        elif choice != '3':
            print("❌ Wrong choice")

        return False

    def settings_menu(self):
        while True:
            print("\n⚙️ PROFILE SETTINGS")
            print("=" * 50)
            print(f"👤 Имя: {self.username}")
            print("1. 🔑 Show public key")
            print("2. 🔄 Change secret phrase")
            print("3. 🗑️ Delete profile")
            print("4. ↩️ Back")

            choice = self.safe_input("\nSelect an action (1-4): ")

            if choice == '1':
                self.show_public_key()
            elif choice == '2':
                self.change_secret()
            elif choice == '3':
                self.delete_profile()
                break
            elif choice == '4':
                break
            else:
                print("❌ Wrong choice")

    def show_public_key(self):
        config = self.db.get_config()
        public_key = config.get('public_key', '')
        print(f"\n🔑 Your public key:")
        print(public_key)
        input("\nPress Enter to continue...")

    def change_secret(self):
        print("\n🔄 CHANGING THE SECRET PHRASE")
        print("=" * 50)

        current_secret = self.safe_input("Enter your current secret phrase: ")
        if not self.auth.verify_secret(self.username, current_secret,
                                       self.db.get_config().get('public_key', '')):
            print("❌ Invalid current phrase")
            return

        new_secret = self.safe_input("Enter a new secret phrase: ")
        if not new_secret:
            print("❌ The new phrase cannot be empty.")
            return

        confirm = self.safe_input("Repeat the new secret phrase: ")
        if new_secret != confirm:
            print("❌ The phrases do not match")
            return

        new_public_key = self.auth.generate_public_key(self.username, new_secret)
        self.db.set_config('public_key', new_public_key)
        self.master_seed = new_secret

        print("✅ Secret phrase changed!")

    def delete_profile(self):
        print("\n❌ DELETE PROFILE")
        print("=" * 50)
        print("⚠️  This action will delete:")
        print("   - All your chats")
        print("   - All messages")
        print("   - Profile settings")
        print("   - Unable to recover!")

        confirm = self.safe_input("\n❌ Enter 'DELETE' to confirm: ")
        if confirm != 'DELETE':
            print("❌ Deletion cancelled")
            return

        db_path = self.config_dir / "clm.db"
        if db_path.exists():
            db_path.unlink()

        print("✅ The profile has been deleted. To use it, please launch the program again..")
        sys.exit(0)

    def create_chat(self):
        print("\n➕ CREATING A NEW CHAT")
        print("=" * 50)

        name = self.safe_input("Enter the chat name: ")
        if not name:
            print("❌ Name is required")
            return

        seed_suffix = self.safe_input("Enter the seed suffix (or Enter for automatic): ")

        chats = self.db.get_chats()
        numeric_ids = [int(k) for k in chats.keys() if k.isdigit()]
        new_id = str(max(numeric_ids) + 1) if numeric_ids else '0'

        if not seed_suffix:
            seed_suffix = f"chat_{new_id}"

        self.db.add_chat(new_id, name, seed_suffix)
        print(f"✅ Chat created: {new_id}: {name}")

    def display_messages(self, messages, show_ids=False):
        for msg in messages:
            self.display_message(msg, show_ids)

        total = len(messages)
        print(f"\n📊 Showing {total} messages")
        input("\nPress Enter to continue...")

    def display_message(self, msg, show_ids=False):
        chat_name = self.get_chat_name(msg['chat_id'])
        time_str = datetime.fromtimestamp(msg['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
        direction = "📤" if msg['type'] == 'sent' else "📥"
        msg_id = f" [#{msg['id']}]" if show_ids else ""

        print(f"\n{direction}{msg_id} [{time_str}] {chat_name}:")
        print(f"   {msg['message']}")

    def display_message_detail(self, msg):
        chat_name = self.get_chat_name(msg['chat_id'])
        time_str = datetime.fromtimestamp(msg['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
        direction = "📤 Sent" if msg['type'] == 'sent' else "📥 Received"
        status = " (🗑️ удалено)" if msg.get('is_deleted', 0) == 1 else ""

        print(f"\n{direction}{status}")
        print(f"ID: #{msg['id']}")
        print(f"Chat: {chat_name}")
        print(f"Time: {time_str}")
        print(f"Content: {msg['message']}")

        if msg['type'] == 'sent' and not msg.get('is_deleted', 0):
            print(f"Pointer: {msg['payload']}")

        input("\nPress Enter to continue...")

    def get_chat_name(self, chat_id: str) -> str:
        chats = self.db.get_chats()
        return chats.get(chat_id, {}).get("name", f"Chat {chat_id}")

    def get_chat_seed_suffix(self, chat_id: str) -> str:
        chats = self.db.get_chats()
        return chats.get(chat_id, {}).get("seed_suffix", f"chat_{chat_id}")

    def send_message(self, message: str, chat_id: str) -> str:
        if not self.master_seed or not self.username:
            raise ValueError("❌ Authentication required")

        epoch_index = int(time.time())
        signed_message = f"{self.username}: {message}"

        chat_seed_suffix = self.get_chat_seed_suffix(chat_id)
        seed_material = f"{self.master_seed}_{chat_seed_suffix}_{epoch_index}".encode()
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

        if not self.master_seed:
            return None, "❌ Authentication required"

        chat_seed_suffix = self.get_chat_seed_suffix(chat_id)
        seed_material = f"{self.master_seed}_{chat_seed_suffix}_{epoch_index}".encode()
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


def main():
    cli = ChronoLibrarianCLI()

    config = cli.db.get_config()
    if 'public_key' not in config:
        print("🌌 Welcome to Chrono-Library Messenger!")
        print("=" * 50)
        if cli.setup():
            if cli.login():
                cli.show_main_menu()
    else:
        if cli.login():
            cli.show_main_menu()


if __name__ == "__main__":
    main()
