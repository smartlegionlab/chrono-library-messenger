# Chrono-Library Messenger (CLM) <sup>v1.1.1</sup>

[![GitHub top language](https://img.shields.io/github/languages/top/smartlegionlab/chrono-library-messenger)](https://github.com/smartlegionlab/chrono-library-messenger)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/chrono-library-messenger?label=pypi%20downloads)](https://pypi.org/project/chrono-library-messenger/)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/smartlegionlab/chrono-library-messenger)](https://github.com/smartlegionlab/chrono-library-messenger/)
[![GitHub](https://img.shields.io/github/license/smartlegionlab/chrono-library-messenger)](https://github.com/smartlegionlab/chrono-library-messenger/blob/master/LICENSE)
[![GitHub Repo stars](https://img.shields.io/github/stars/smartlegionlab/chrono-library-messenger?style=social)](https://github.com/smartlegionlab/chrono-library-messenger/)
[![GitHub watchers](https://img.shields.io/github/watchers/smartlegionlab/chrono-library-messenger?style=social)](https://github.com/smartlegionlab/chrono-library-messenger/)
[![GitHub forks](https://img.shields.io/github/forks/smartlegionlab/chrono-library-messenger?style=social)](https://github.com/smartlegionlab/chrono-library-messenger/)

## 🌌 The Messaging Protocol That Transmits Nothing

A revolutionary Python CLI tool implementing a cryptographic paradigm where **messages are not sent but discovered**. Based on the radical concept that communication doesn't require data transmission—only synchronized access to a shared mathematical space.

> **✨ Philosophical Foundation:** This tool implements the paradigm-shifting ideas explored in my articles: [Chrono-Library Messenger](https://dev.to/smartlegionlab/i-created-a-messenger-that-doesnt-send-any-data-heres-how-it-works-4ecp) and [Messages That Have Always Been With Us](https://dev.to/smartlegionlab/the-magic-of-messages-that-have-always-been-with-us-48gp). Your messages aren't transmitted—they're mathematical truths that emerge when accessed synchronously.

## 🌟 Revolutionary Features

- 🚫 **Zero Data Transmission** - Only public pointers are shared, no message content
- 🔒 **Cryptographically Secure** - HMAC-SHA256 DRBG for deterministic generation
- 👤 **Built-in Identity** - Messages automatically signed with username
- 💬 **Chat Realms** - Separate encrypted spaces for different conversations
- ⏳ **Asynchronous & Eternal** - Messages decodable years after creation
- 🕵️ **Plausible Deniability** - Pointers indistinguishable from random noise
- 💾 **Local History** - Complete message history stored only on your device

---

## 🌌 The Paradox at the Core

This tool embodies a beautiful cryptographic paradox: **synchronous discovery without transmission**. 

The system enables:
- **Perfect synchronization** - Identical inputs (secret + timestamp + chat) produce identical message extraction
- **Complete opacity** - Without the exact inputs, pointers are computationally meaningless noise
- **Zero transmission** - Message content never leaves the local device

This paradox is powered by deterministic cryptography - the same revolutionary concept explored in our foundational articles:
- [**Chrono-Library Messenger**](https://dev.to/smartlegionlab/i-created-a-messenger-that-doesnt-send-any-data-heres-how-it-works-4ecp) - The core implementation details
- [**Messages That Have Always Been With Us**](https://dev.to/smartlegionlab/the-magic-of-messages-that-have-always-been-with-us-48gp) - Philosophical foundation
- [**The Password That Never Was**](https://dev.to/smartlegionlab/the-password-that-never-was-how-to-access-secrets-that-were-always-there-smart-password-library-4h16) - Related deterministic security concepts

Your messages don't need to be transmitted because they were never created—they already exist as mathematical certainties, waiting to be discovered through synchronized access to the shared Chrono-Library.

---

## 📦 Installation

```bash
pip install chrono-library-messenger
```

## 🧙‍♂️ Quick Start: Discover Your First Message

### 1. Initial Setup
```bash
clm setup --username "@yourname" --master-seed "OurSharedSecretPhrase123!"
```

### 2. View Available Chat Realms
```bash
clm chats
```
```
💬 Available chats:
  0: ⚡️ Urgent
  1: 💬 General chat
  2: 🤫 Secrets
```

### 3. Send a Message (Discover and Share Pointer)
```bash
clm send "Hello! How are you?" --chat 1
```
```json
{"c": "1", "e": 1736854567, "d": "8d3e12a45b..."}
```

### 4. Receive a Message (Discover from Pointer)
```bash
clm receive '{"c": "1", "e": 1736854567, "d": "8d3e12a45b..."}'
```
```
✅ Message received!
@yourname: Hello! How are you?
```

## 🏗️ Core Architecture

### The Chrono-Library Protocol
1. **Eternal Library**: Shared secret generates deterministic, infinite pseudorandom sequences
2. **Chat Realms**: Unique seed suffixes create isolated spaces within the library
3. **Time as Index**: Unix timestamp ensures unique keys for every message
4. **Synchronous Discovery**: Both parties extract messages using identical parameters

### Cryptographic Foundation
- **HMAC_DRBG**: Cryptographically secure deterministic random bit generator
- **SHA-256**: Industry-standard cryptographic hashing
- **XOR Cipher**: Perfect secrecy when key is truly random
- **Deterministic Generation**: Reproducible outputs from identical inputs

## 🔄 Ecosystem Integration

### Complementary Tools
- [**SmartPassLib**](https://github.com/smartlegionlab/smartpasslib/) - Core deterministic password generation
- [**CLI PassGen**](https://github.com/smartlegionlab/clipassgen/) - Console password discovery
- [**CLI PassMan**](https://github.com/smartlegionlab/clipassman/) - Console password manager

### Consistency Framework
Messages discovered with CLM follow the same deterministic principles as the broader smart security ecosystem.

## 🛡️ Security Architecture

### What's Shared (Public)
- Chat ID (`c`)
- Timestamp (`e`) 
- Ciphertext (`d`)

### What's Never Shared (Private)
- Master secret phrase
- Message content
- Decryption keys
- Username signatures

### Threat Mitigation
- **No Central Servers**: Eliminates service provider risks
- **Channel Agnosticism**: Pointers can be shared via any medium
- **Plausible Deniability**: Pointers resemble random application data
- **Local Storage**: All data remains on user devices

## 📖 Advanced Usage

### Message History Management
```bash
# View complete message history
clm history

# Show messages with public pointers
clm history --show-pointers

# Filter by chat realm
clm history --chat 1

# Include deleted messages
clm history --show-deleted
```

### Chat Realm Management
```bash
# Create new chat realm
clm add-chat "💬 Private Communications"

# Delete chat and all messages
clm delete-chat "3"

# Clear chat history
clm clear-history --chat "1"
```

### Message Management
```bash
# Delete message (move to trash)
clm delete-message 42

# Permanently delete message
clm delete-message 42 --permanent

# Restore deleted message
clm restore-message 42
```

## 🌐 Philosophical Foundation

This implementation isn't just code—it's a new way of thinking about communication. Read the foundational articles:

1. [**Chrono-Library Messenger: How to send a message without transmitting a single bit**](https://dev.to/smartlegionlab/i-created-a-messenger-that-doesnt-send-any-data-heres-how-it-works-4ecp) - Technical implementation
2. [**The magic of messages that have always been with us**](https://dev.to/smartlegionlab/the-magic-of-messages-that-have-always-been-with-us-48gp) - Philosophical basis
3. [**The Password That Never Was**](https://dev.to/smartlegionlab/the-password-that-never-was-how-to-access-secrets-that-were-always-there-smart-password-library-4h16) - Related deterministic security concepts

## ⚠️ Security Considerations

**Important: This is a Proof-of-Concept (PoC) and research project.**

While built on strong cryptographic primitives, this implementation **has not undergone formal security audit**. Use for experimentation and education, not for protecting truly sensitive information.

### Known Limitations
- **Metadata Exposure**: Chat IDs and timestamps are public
- **Pre-Shared Secret Requirement**: Initial key exchange needed
- **No Forward Secrecy**: Master secret compromise reveals all messages
- **No Integrity Protection**: Basic protocol lacks message authentication

## 🤝 Supported Platforms

- **Linux** - All major distributions
- **Windows** - 7, 8, 10, 11
- **macOS** - Fully supported
- **Android** - Via Termux

## 📊 Database Structure

All data stored locally in SQLite format:
- Location: `~/.config/clm/clm.db`
- Tables: `config`, `chats`, `messages`
- Encryption: No database encryption (local device security only)

## 🚀 Production Considerations

For serious use, consider:
- Secure master secret exchange protocol
- Additional integrity protection
- Forward secrecy mechanisms
- Database encryption
- Formal security audit

## 📜 License & Disclaimer

BSD 3-Clause License

Copyright (c) 2025, Alexander Suvorov

```
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```

**Legal Disclaimer:** Chrono-Library Messenger is a proof-of-concept for academic research and educational purposes only. Users are solely responsible for compliance with all applicable laws and regulations.

## 🌟 Join the Communication Revolution

This isn't just another messaging tool—it's a fundamental shift from **transmitting information** to **discovering mathematical truths**. Your messages were always there. Now you know how to find them.

**What do you think? Is this the future of secure communication? Or just beautiful mathematical poetry?** Let's discuss on [Dev.to](https://dev.to/smartlegionlab) or [GitHub](https://github.com/smartlegionlab/chrono-library-messenger)!

---

*Discover more revolutionary projects at [Smart Legion Lab](https://github.com/smartlegionlab)*

