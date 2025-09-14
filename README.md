# Chrono-Library Messenger (CLM)

---

![GitHub top language](https://img.shields.io/github/languages/top/smartlegionlab/chrono-library-messenger)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/chrono-library-messenger?label=pypi%20downloads)](https://pypi.org/project/chrono-library-messenger/)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/smartlegionlab/chrono-library-messenger)](https://github.com/smartlegionlab/chrono-library-messenger/)
[![GitHub](https://img.shields.io/github/license/smartlegionlab/chrono-library-messenger)](https://github.com/smartlegionlab/chrono-library-messenger/blob/master/LICENSE)
[![GitHub Repo stars](https://img.shields.io/github/stars/smartlegionlab/chrono-library-messenger?style=social)](https://github.com/smartlegionlab/chrono-library-messenger/)
[![GitHub watchers](https://img.shields.io/github/watchers/smartlegionlab/chrono-library-messenger?style=social)](https://github.com/smartlegionlab/chrono-library-messenger/)
[![GitHub forks](https://img.shields.io/github/forks/smartlegionlab/chrono-library-messenger?style=social)](https://github.com/smartlegionlab/chrono-library-messenger/)

---

**A messaging protocol without data transmission. Communication through synchronized extraction from an Eternal Library.**

## The Magic

CLM implements a radical new communication paradigm. **There is no act of data transmission.** Instead, two parties synchronously extract information from a shared, predetermined pseudorandom sequence (the "Eternal Library") using public "pointers."

You don't send messages. You **publish coordinates**. The recipient **recreates the message locally** using the same coordinates and shared secret.

---

## 🔐 Security Considerations & Status

**Important: This is a Proof-of-Concept (PoC) and a research project.**

While the concept is built on cryptographic primitives, this implementation **has not undergone a formal security audit**. Use it for experimentation and educational purposes, not for protecting truly sensitive information.

### Known Limitations & Threats

*   **Metadata Exposure:** The pointers `{"c": chat_id, "e": timestamp, "d": ciphertext}` are public. An observer can see who is communicating (by analyzing pointer patterns), when, and how frequently. The chat IDs are not encrypted.
*   **Pre-Shared Secret Requirement:** The protocol requires a pre-shared master seed, which must be exchanged over a secure channel (e.g., in person via Signal/Keybase) beforehand. This doesn't solve the initial key exchange problem.
*   **Master Seed Compromise:** If the master seed is compromised, **all messages across all chats** can be decrypted by an adversary.
*   **Deterministic Key Generation:** The security relies heavily on the robustness of the HMAC-DRBG implementation. Any flaw in the construction could lead to key material reuse or predictability.
*   **Denial-of-Service:** Since the channel for sharing pointers is public, an attacker can flood it with garbage pointers, making it hard to find legitimate messages.

### Why Publish?

This project was published to:
*   Stimulate discussion about alternative communication paradigms.
*   Demonstrate the concept of "communication without transmission."

---

## How It Works

1.  **The Eternal Library:** A shared master seed phrase generates deterministic, infinite pseudorandom sequences.
2.  **Personal Chat Realms:** Each chat has a unique seed suffix, creating separate "realms" within the library.
3.  **Sending:**
    *   Your message is automatically signed with your username.
    *   A key is generated from: `master_seed + chat_seed_suffix + timestamp`
    *   The signed message is encrypted with the key (XOR) to create a ciphertext.
    *   Only the pointer `{"c": "chat_id", "e": timestamp, "d": "ciphertext"}` is published.
4.  **Receiving:**
    *   The recipient finds the pointer.
    *   They regenerate the same key using their identical master seed and chat suffix.
    *   They decrypt the ciphertext to reveal the signed message: `@username: Your message here`.

## Key Features

*   **🚫 No Data Transmission:** Only public pointers (random-looking JSON) are shared.
*   **👤 Built-in Identity:** Messages are automatically signed with your username.
*   **💬 Personal Chats:** Create separate chat realms for different conversations.
*   **⏳ Asynchronous & Eternal:** Messages can be decoded years after they were created.
*   **🕵️ Plausible Deniability:** Pointers are indistinguishable from random noise.
*   **💾 Local History:** Complete history of all sent and received messages.

## Installation & Setup

1.  **Ensure Python 3.6+ is installed.**
2.  **Download the script:**
3.  **Initial Setup:**
    ```bash
    python clm.py setup --username "@yourname" --master-seed "OurSharedSecretPhrase123!"
    ```

## Usage

### 1. View Available Chats
```bash
python clm.py chats
```

Output:

```
💬 Available chats:
  0: ⚡️ Urgent
  1: 💬 General chat
  2: 🤫 Secrets
```

2. Send a Message to a Chat

```bash
python clm.py send "Hello! How are you?" --chat 1
```

Output: A JSON pointer to share publicly.

```json
{"c": "1", "e": 1736854567, "d": "8d3e12a45b..."}
```

3. Receive a Message

```bash
python clm.py receive '{"c": "1", "e": 1736854567, "d": "8d3e12a45b..."}'
```

Output: The decrypted, signed message:

```
✅ Message received!
@yourname: Hello! How are you?
```

4. View Conversation History

```bash
# Show all messages from all chats
python clm.py history

# Show messages only from specific chat
python clm.py history --chat 1

# Show messages with public pointers (for debugging)
python clm.py history --show-pointers
```

5. Create a New Chat

```bash
# Create a chat with auto-generated seed suffix
python clm.py add-chat "💬 Private Chat with Alice"

# Create a chat with custom seed suffix
python clm.py add-chat "💼 Work Projects" --seed-suffix "work_projects"
```

Example Session

```bash
# Setup profile
$ python clm.py setup --username "@sid" --master-seed "magic_secret_123"
✅ Configuration saved!
👤 Your username: @sid
💬 Available chats:
  0: ⚡️ Urgent
  1: 💬 General chat
  2: 🤫 Secrets

# Send message to general chat
$ python clm.py send "Hello everyone! 👋" --chat 1
✅ Message saved to history!
📤 Public pointer (for sharing):
{"c": "1", "e": 1736854567, "d": "a1b2c3d4e5f6..."}

# Receive a message
$ python clm.py receive '{"c": "1", "e": 1736854668, "d": "f7g8h9i0j1k2..."}'
✅ Message received!
@nancy: Hi Sid! How are you doing?

# View history
$ python clm.py history --chat 1
📤 [2025-01-14 12:42:47] 💬 Общий чат:
@sid: Hello everyone! 👋

📥 [2025-01-14 12:44:28] 💬 Общий чат:
@nancy: Hi Sid! How are you doing?

# Create new chat
$ python clm.py add-chat "💬 Private Chat with Bob"
✅ New chat added: 3: 💬 Private Chat with Bob
```

Chat Management

Default Chats

· 0: ⚡️ Urgent - For urgent messages
· 1: 💬 General chat - General conversation channel
· 2: 🤫 Secrets - For sensitive discussions

Creating Private Chats

For private conversations, create a new chat and share the chat ID with your contact:

```bash
python clm.py add-chat "💬 Alice Private"
# Share chat ID 3 with Alice, and make sure she uses the same chat ID
```

Security Model

· Master Seed is Sacred: Protect your master seed phrase. Anyone with it can read all your messages.
· Chat Isolation: Each chat's sequence is isolated. Compromising one chat doesn't affect others.
· Pointer Metadata: Chat IDs and timestamps are public. Message content and authorship remain secret until decryption.
· No Time Intervals: Each message uses exact timestamp as a unique coordinate, making every message truly unique.

File Structure

```
~/.config/clm/
├── config.json          # Your username and master seed
├── chats.json           # Chat definitions and seed suffixes
├── sent/                # All messages you've sent
└── received/            # All messages you've received
```

FAQ

Q: How do I start a private conversation with someone? A:Create a new chat with add-chat, share the chat ID with them, and ensure they use the same chat ID and master seed.

Q: Can someone see who I'm talking to? A:Yes, chat IDs in pointers are public. For private conversations, use less obvious chat IDs or create multiple chats.

Q: What if I want to change my username? A:Edit ~/.config/clm/config.json and change the username field. Old messages will still show your old username.

Q: Is this secure for sensitive information? A:The protocol uses strong cryptography (HMAC-SHA256), but is a novel design. For critical secrets, use established tools like Signal.

Disclaimer

This tool is intended for educational and research purposes to explore new paradigms in communication. The authors are not responsible for how it is used.

```

### Quick cheat sheet on usage:

```bash
# Setup
python clm.py setup --username "@mylogin" --master-seed "our_secret"

# View chats
python clm.py chats

# Send to general chat (ID=1)
python clm.py send "Hello!" --chat 1

# Receive message
python clm.py receive '{"c": "1", "e": 1736854567, "d": "a1b2c3..."}'

# General chat history
python clm.py history --chat 1

# Create new chat
python clm.py add-chat "💬 Private chat"
```

---

## 📜 License & Disclaimer

This project is licensed under the **GNU Affero General Public License v3.0 (AGPLv3)**.

- You are free to use, modify, and distribute this software.
- **However, if you modify this software and run it as a hosted service (e.g., a web app), you MUST make the full source code of your modified version available to your users under the same license.**
- The full license text can be found in the [LICENSE](https://github.com/smartlegionlab/chrono-library-messenger/blob/master/LICENSE) file.

### ⚠️ Important Disclaimer

> **THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.**
>
> *(This is a summary of the full disclaimer, which is legally binding and located in sections 15 and 16 of the AGPLv3 license).*

For commercial use that is not compatible with the AGPLv3 terms (e.g., including this software in a proprietary product without disclosing the source code), a **commercial license** is required. Please contact me at [smartlegiondev@gmail.com](mailto:smartlegiondev@gmail.com) to discuss terms.
