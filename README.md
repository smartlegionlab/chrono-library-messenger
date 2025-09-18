# Chrono-Library Messenger (CLM) <sup>v2.0.1</sup>

[![GitHub top language](https://img.shields.io/github/languages/top/smartlegionlab/chrono-library-messenger)](https://github.com/smartlegionlab/chrono-library-messenger)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/chrono-library-messenger?label=pypi%20downloads)](https://pypi.org/project/chrono-library-messenger/)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/smartlegionlab/chrono-library-messenger)](https://github.com/smartlegionlab/chrono-library-messenger/)
[![GitHub](https://img.shields.io/github/license/smartlegionlab/chrono-library-messenger)](https://github.com/smartlegionlab/chrono-library-messenger/blob/master/LICENSE)

## 🌌 The Messaging Protocol That Transmits Nothing & Stores Nothing

A revolutionary Python console application implementing a cryptographic paradigm where **messages are not sent but discovered, and secrets are not stored but verified**. Based on the radical concept that secure communication requires neither data transmission nor secret storage.

> **✨ Philosophical Foundation:** This tool implements the paradigm-shifting ideas from [Chrono-Library Messenger](https://dev.to/smartlegionlab/i-created-a-messenger-that-doesnt-send-any-data-heres-how-it-works-4ecp) and [Messages That Have Always Been With Us](https://dev.to/smartlegionlab/the-magic-of-messages-that-have-always-been-with-us-48gp). Your messages aren't transmitted and your secrets aren't stored—they're mathematical truths waiting to be discovered.

## 🚀 What's New in v2.0

- **🔐 Zero Secret Storage** - Master secrets never persist on disk
- **🎯 Interactive Console UI** - Full-featured menu system instead of CLI commands
- **💬 Real Chat Management** - Create, view, and manage chat rooms
- **📱 Cross-Platform** - Works everywhere Python runs
- **🛡️ Enhanced Security** - Public key authentication without secret exposure

## 🌟 Revolutionary Features

- 🚫 **Zero Data Transmission** - Only public pointers are shared
- 🔒 **Zero Secret Storage** - Master phrase exists only in memory during session
- 📱 **Interactive Console Interface** - Intuitive menu navigation
- 👤 **Identity-Based Messaging** - Automatic sender verification
- 💬 **Multiple Chat Realms** - Organized conversation spaces
- ⏳ **Eternal Message Access** - Decode messages years later
- 🗑️ **Message Recovery** - Restore accidentally deleted messages
- 💾 **Local History Only** - Complete control over your data

![CLI Interface](https://github.com/smartlegionlab/chrono-library-messenger/raw/master/data/images/clm.png)

---

## 🔐 The Authentication Revolution

### How It Works:
1. **Setup**: Create username + master phrase → generates public key
2. **Storage**: Only public key is saved (NOT the master phrase)
3. **Login**: Enter master phrase → generates public key → matches stored key
4. **Session**: Master phrase exists only in RAM during active session
5. **Exit**: Master phrase completely erased from memory

### Security Advantages:
- 🔒 **Breach-Proof**: Database theft reveals nothing valuable
- 🚫 **No Secret Residue**: Master phrase never touches persistent storage
- 🔑 **Cryptographic Proof**: Zero-knowledge style authentication
- ⚡ **Session-Based**: Compromised session doesn't compromise future security

---

## 📦 Installation

```bash
pip install chrono-library-messenger
```

## 🧙‍♂️ Quick Start: Your First Session

### 1. First Launch - Initial Setup
```bash
clm
```
The application will guide you through:
- Creating your username
- Setting your master secret phrase
- Generating secure public key

### 2. Normal Usage - Secure Authentication
```bash
clm
```
Enter your secret phrase to access your messages. The phrase is verified against the stored public key without ever storing the secret itself.

### 3. Main Features Discovered Through Menu:
- 💬 **My Chats** - Browse and manage conversation spaces
- 📨 **Send Messages** - Create and share message pointers
- 📩 **Receive Messages** - Decode messages from pointers
- 📜 **Message History** - View your conversation history
- ⚙️ **Profile Settings** - Manage security settings

## 🏗️ Core Architecture

### The Double Paradox:
1. **Synchronous Discovery Without Transmission**
   - Messages emerge from mathematical space when parameters align
   - No content ever leaves your device

2. **Authentication Without Storage**
   - Prove knowledge without revealing the secret
   - Verify identity without storing credentials

### Cryptographic Foundation:
- **HMAC_DRBG** - NIST-compliant deterministic random bit generator
- **SHA-256** - Industry-standard cryptographic hashing
- **XOR Cipher** - Information-theoretic security when key is random
- **Public Key Auth** - Proof-of-knowledge without secret exposure

## 🛡️ Security Architecture

### What's Stored (Safe):
- `public_key` - Cryptographic proof of secret knowledge
- `username` - Your public identity
- `message_history` - Your local conversation records
- `chat_configs` - Your conversation space settings

### What's NEVER Stored (Secure):
- `master_secret` - Your authentication phrase
- `decryption_keys` - Message decryption material
- `session_tokens` - Temporary access credentials

### What's Shared (Public):
- `pointers` - JSON objects containing (chat_id, timestamp, ciphertext)
- `chat_ids` - Public conversation identifiers
- `timestamps` - Message discovery time references

## 📖 Advanced Usage

### Interactive Console Features:

**Chat Management:**
```bash
# Create dedicated conversation spaces
+ Private Discussions
+ Team Channels  
+ Project Rooms
```

**Message Recovery:**
```bash
# Restore accidentally deleted messages
🗑️ Basket → Restore deleted items
```

**Security Management:**
```bash
# Change secrets without exposure
⚙️ Settings → Change secret phrase
```

**History Navigation:**
```bash
# Browse through time
📜 History → Filter by chat → View conversations
```

## 🔄 Ecosystem Integration

### Built on Proven Foundations:
- **[SmartPassLib](https://github.com/smartlegionlab/smartpasslib/)** - Deterministic cryptography core
- **Zero-Storage Principle** - No secrets, no problems
- **Cross-Platform Compatibility** - Universal Python implementation

### Consistency Framework:
All components follow the same security principles:
- Deterministic cryptography
- Zero secret storage
- Local data ownership
- User-controlled access

## ⚠️ Security Considerations

**Important: This remains a Proof-of-Concept for research and education.**

### Enhanced Security in v2.0:
- ✅ **No secret storage** - Master phrases never persisted
- ✅ **Session-only memory** - Secrets exist only during active use
- ✅ **Public key verification** - Cryptographic proof without exposure
- ✅ **Local data control** - Everything stays on your device

### Current Limitations:
- **Metadata Visibility** - Chat IDs and timestamps remain public
- **Pre-Shared Knowledge** - Initial secret phrase must be established securely
- **No Forward Secrecy** - Master phrase compromise reveals historical messages
- **Basic Integrity** - Additional authentication codes could enhance protection

## 🤝 Supported Platforms

- **Linux** - Native console support
- **Windows** - Command Prompt and PowerShell
- **macOS** - Terminal and iTerm2
- **Android** - Termux environment
- **BSD** - Full compatibility

## 📊 Database Structure

**Location**: `~/.config/clm/clm.db` (fully portable)

**Tables**:
- `config` - Public key and username (NO SECRETS)
- `chats` - Conversation space definitions
- `messages` - Encrypted message history

**Security**: No database encryption - relies on system security

## 🚀 Production Considerations

For serious deployment consider adding:
- Database encryption layer
- Secure secret exchange protocol
- Forward secrecy mechanisms
- Message authentication codes
- Formal security audit
- Backup and recovery procedures

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

**Legal Disclaimer:** Chrono-Library Messenger is a proof-of-concept for academic research and educational purposes only. Users are solely responsible for compliance with all applicable laws and regulations regarding cryptography and secure communications in their jurisdiction.

## 🌟 Join the Security Revolution

This isn't just another messaging app—it's a fundamental rethinking of digital security:

**From storing secrets → to proving knowledge**  
**From transmitting data → to discovering truths**  
**From trusting providers → to owning your security**

Your messages were always there. Your security was always possible. Now you have the tools to discover both.

**What do you think? Is this the future of digital security? Let's discuss on [Dev.to](https://dev.to/smartlegionlab) or [GitHub](https://github.com/smartlegionlab/chrono-library-messenger)!**

---

*Discover more revolutionary projects at [Smart Legion Lab](https://github.com/smartlegionlab)*

## 🔧 Development & Contributing

```bash
# Setup development environment
git clone https://github.com/smartlegionlab/chrono-library-messenger.git
cd chrono-library-messenger
pip install -e .

# Contribution welcome!
# Focus areas: security audit, UI improvements, documentation
```

*Together, we're building a future where security means never having to store a secret.*
