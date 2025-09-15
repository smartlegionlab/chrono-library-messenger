# Chrono-Library Messenger (CLM) <sup>v1.0.1</sup>

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

### 🧠 How it works: Magic without data transfer

CLM implements a radically new communication paradigm. **There is no act of data transfer.** Instead, two parties synchronously extract information from a shared, predetermined pseudo-random data stream - the "Eternal Library" - using public "pointers".

You don't send messages. You **publish coordinates**. The recipient **recreates the message locally** using the same coordinates and a shared secret.

#### How does it work?

1. **Eternal Library:** A shared seed generates a deterministic, infinite pseudo-random sequence - our "library".
2. **Library Partitions (Chats):** Each chat has a unique seed suffix, creating an isolated "partition" within the library.
3. **The "sending" process:**
* Your message is automatically signed with your username.
* The encryption key is generated from the combination: `master phrase + chat_suffix + timestamp`.
* The signed message is encrypted with this key (XORed) and turned into ciphertext.
* Only the **pointer** is published - the JSON object `{"c": "chat_id", "e": timestamp, "d": "ciphertext"}`.
4. **The "receiving" process:**
* The receiver finds the pointer.
* Using the identical master phrase and chat suffix, it **recreates the same key** for the specified timestamp.
* It applies the key to the ciphertext (XORed again) and decrypts the original signed message: `@username: Your message here`.

**The message never left the sender's device.** Only the pointer was transmitted to the recipient's device. The message itself was "extracted" from the shared, pre-synchronized data structure.

#### 🛡️ Key benefits and implications:

* **💨 Does not require internet:** No internet or mobile connection is required for exchange**. Pointers can be transmitted **in any way**: written on a piece of paper, sent via SMS, posted on social networks, transmitted via messengers, QR code or radio signal.
* **👻 Metadata anonymity:** The pointer looks like a random set of data. For an outside observer, it is **impossible to prove** that this is a message at all and not technical garbage.
* **🛡️ Resistance to attacks:** Classic attacks (MITM, DDoS) are meaningless. **It is impossible to intercept or replace a message** — you can only prevent the transmission of a pointer, which can be easily sent another way. There is no central server that can be attacked.
* **📦 Locality and sovereignty:** All data is stored only on your device. **No providers, servers, or third parties** that can access your correspondence.
* **⏳ Eternity:** A message can be decrypted years and decades after it was sent. It is enough to save the common master phrase and pointer. No dependence on working services or protocol updates.

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

## Installation

### From PyPI (recommended)
```bash
pip install chrono-library-messenger
```

### From source
```bash
git clone https://github.com/smartlegionlab/chrono-library-messenger.git
cd chrono-library-messenger
pip install .
```

## Usage

### 1. Initial Setup
```bash
clm setup --username "@yourname" --master-seed "OurSharedSecretPhrase123!"
```

### 2. View Available Chats
```bash
clm chats
```

Output:
```
💬 Available chats:
  0: ⚡️ Urgent
  1: 💬 General chat
  2: 🤫 Secrets
```

### 3. Send a Message to a Chat
```bash
clm send "Hello! How are you?" --chat 1
```

Output: A JSON pointer to share publicly.
```json
{"c": "1", "e": 1736854567, "d": "8d3e12a45b..."}
```

### 4. Receive a Message
```bash
clm receive '{"c": "1", "e": 1736854567, "d": "8d3e12a45b..."}'
```

Output: The decrypted, signed message:
```
✅ Message received!
@yourname: Hello! How are you?
```

### 5. View Conversation History
```bash
# Show all messages from all chats
clm history

# Show messages only from specific chat
clm history --chat 1

# Show messages with public pointers
clm history --show-pointers

# Limit number of messages shown
clm history --limit 10
```

### 6. Create a New Chat
```bash
# Create a chat with auto-generated seed suffix
clm add-chat "💬 Private Chat with Alice"

# Create a chat with custom seed suffix
clm add-chat "💼 Work Projects" --seed-suffix "work_projects"
```

## Running from source without installation

```bash
# From project root directory
python -m clm setup --username "@user" --master-seed "secret"
python -m clm send "Hello" --chat 1
python -m clm history --chat 1
```

## Example Session

```bash
# Setup profile
$ clm setup --username "@sid" --master-seed "magic_secret_123"
✅ Configuration saved!
👤 Your username: @sid
💬 Available chats:
  0: ⚡️ Urgent
  1: 💬 General chat
  2: 🤫 Secrets

# Send message to general chat
$ clm send "Hello everyone! 👋" --chat 1
✅ Message saved!
📤 Public pointer:
{"c": "1", "e": 1736854567, "d": "a1b2c3d4e5f6..."}

# Receive a message
$ clm receive '{"c": "1", "e": 1736854668, "d": "f7g8h9i0j1k2..."}'
✅ Message received!
@nancy: Hi Sid! How are you doing?

# View history
$ clm history --chat 1
📤 [2025-01-14 12:42:47] 💬 General chat:
@sid: Hello everyone! 👋

📥 [2025-01-14 12:44:28] 💬 General chat:
@nancy: Hi Sid! How are you doing?

# Create new chat
$ clm add-chat "💬 Private Chat with Bob"
✅ Chat added: 3: 💬 Private Chat with Bob
```

## Chat Management

### Default Chats
- **0: ⚡️ Urgent** - For urgent messages
- **1: 💬 General chat** - General conversation channel  
- **2: 🤫 Secrets** - For sensitive discussions

### Creating Private Chats
For private conversations, create a new chat and share the chat ID with your contact:
```bash
clm add-chat "💬 Alice Private"
# Share chat ID 3 with Alice, and make sure she uses the same chat ID
```

## Database Location
All data is stored in SQLite format: `~/.config/clm/clm.db`

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
*   Get feedback from the security and open-source community.
*   Serve as an educational resource for those interested in cryptography and protocol design.

## FAQ

**Q: How do I start a private conversation with someone?**
A: Create a new chat with `add-chat`, share the chat ID with them, and ensure they use the same chat ID and master seed.

**Q: Can someone see who I'm talking to?**
A: Yes, chat IDs in pointers are public. For private conversations, use less obvious chat IDs or create multiple chats.

**Q: What if I want to change my username?**
A: Your username is stored in the database and used for message signing. Old messages will still show your old username.

**Q: Is this secure for sensitive information?**
A: The protocol uses strong cryptography (HMAC-SHA256), but is a novel design. For critical secrets, use established tools like Signal.

## Quick Cheat Sheet

```bash
# Setup
clm setup --username "@mylogin" --master-seed "our_secret"

# View chats
clm chats

# Send to general chat (ID=1)
clm send "Hello!" --chat 1

# Receive message
clm receive '{"c": "1", "e": 1736854567, "d": "a1b2c3..."}'

# General chat history
clm history --chat 1

# Create new chat
clm add-chat "💬 Private chat"
```

## New commands:

### Delete/Soft delete/Clear chats and messages

- `clm delete-chat <chat_id> - delete chat and all messages`
- `clm delete-message <id> - delete message (to trash)`
- `clm delete-message <id> --permanent - delete permanently`
- `clm restore-message <id> - restore message`
- `clm clear-history --chat <chat_id> - clear chat history`
- `clm history --show-ids - show message IDs`
- `clm history --show-deleted - show deleted messages`

---

**I was inspired by my other projects:**

[smartpasslib](https://github.com/smartlegionlab/smartpasslib) - A cross-platform Python library for generating deterministic, secure passwords that never need to be stored.

[clipassman](https://github.com/smartlegionlab/clipassman) - Cross-platform console Smart Password manager and generator.

[Smart Babylon Library](https://github.com/smartlegionlab/smart-babylon-library) - A Python library inspired by the Babylonian Library and my concept of smart passwords. It generates unique addresses for texts without physically storing them, allowing you to retrieve information using these addresses.

---

**📜 Legal & Ethical Disclaimer:**

Chrono-Library Messenger (CLM) is a proof-of-concept project created for academic, research, 
and educational purposes only. It is designed to explore alternative paradigms in communication technology. 
The author does not encourage or condone the use of this tool for any illegal activities 
or to violate the laws of any country. The mention of other messaging services is 
made for comparative analysis within a technological context and constitutes fair use. 
Users are solely responsible for ensuring their compliance with all applicable local, 
national, and international laws and regulations.