<div align="center">
<h1>🛡️ COMRADE: Zero-Trust Local Vault</h1>

<h4>Cyber Operations Module for Resilient Authentication and Data Encryption</h4>

![Version](https://img.shields.io/badge/version-1.0.2-ff8c00)
![License](https://img.shields.io/badge/license-MIT-white)
![Security](https://img.shields.io/badge/encryption-AES--256--GCM-00ffff)
![Platform](https://img.shields.io/badge/platform-CLI/GUI-blue)

<h6>COMRADE is a high-security, local-first encryption engine designed for developers and privacy advocates. It ensures that sensitive documents, source code, and private data are mathematically protected via industry-standard cryptographic protocols, ensuring your data remains yours alone</h6>

</div>

----------------------------------------------------------------------------------------------------------------------------

✨ Features
AES-256-GCM Encryption: Implements Galois/Counter Mode for authenticated encryption, providing both data confidentiality and authenticity (tamper-proofing).

Cryptographic File Masking: Encrypted assets are renamed to random hexadecimal strings, obfuscating metadata, original file types, and intent.

PBKDF2 Key Derivation: Hardens security against brute-force attempts using high-iteration salt stretching for Master Passwords.

Hybrid Interface: Switch seamlessly between a high-speed CLI for automated workflows and a Modern GUI (CustomTkinter) for daily use.

Privacy First: Zero-telemetry, zero-cloud. No data ever leaves your local machine.

🛠️ Project Structure

```powershell
COMRADE/
├── core/          # The Cryptographic Engine (AES logic & File I/O)
├── cli/           # Terminal interface, banners, and command handling
├── ui/            # CustomTkinter dashboard for the visual interface
├── vault/         # Secure storage directory for encrypted .vault files
├── main.py        # Application entry point
└── requirements.txt
```
🚀 Installation
1. Prerequisites
Python: 3.10 or higher

Git: To clone the repository

2. Setup Environment
Open PowerShell (or your preferred terminal) and execute:
```powershell
# Clone the repository
git clone https://github.com/zfln-rehan0520/COMRADE.git
cd COMRADE

# Initialize Virtual Environment
python -m venv venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\venv\Scripts\Activate.ps1

# Install Dependencies
pip install -r requirements.txt
```

🏗️ Usage
----------------------------------------------------------------------------------------------------------------------------
Command Line Interface (CLI)

Ensure your virtual environment is active before running commands.

Action,Command
```powershell

List vault contents :- python main.py --list
Encrypt a file :- python main.py --secure "path/to/file.txt"
Decrypt/Restore :- python main.py --extract <VAULT_ID>.vault
Delete File :-  python main.py --remove  <VAULT_ID>.vault

```
[!NOTE]
When securing a file, the original remains untouched for safety. We recommend manually deleting the source file only after verifying the encryption.
----------------------------------------------------------------------------------------------------------------------------
Graphical User Interface (GUI)
For a visual dashboard experience, launch the application without flags:

```powershell
python main.py
```
<h2>🔒 Security Architecture</h2>

COMRADE is engineered on a Zero-Knowledge and Local-First philosophy. The architecture ensures that the application never possesses the means to decrypt your data without your active input.
```powershell
1. Key Derivation Function (KDF)
To prevent dictionary and brute-force attacks, COMRADE does not use your password directly as an encryption key.

Algorithm: PBKDF2 (Password-Based Key Derivation Function 2).

Entropy: Your Master Password is combined with a cryptographic salt unique to your vault.

Output: Generates a high-entropy 256-bit Key used for the AES cipher.

2. Authenticated Encryption

We utilize AES-256-GCM (Galois/Counter Mode), which is the gold standard for high-performance authenticated encryption.

Confidentiality: Standard AES-256 encryption.

Integrity: The GCM tag ensures that if even a single bit of the encrypted file is altered (bit-flipping attacks), the system will detect the tampering and refuse to decrypt.

Replay Protection: A unique Nonce (Number used Once) is generated for every encryption session, ensuring that the same file encrypted twice will result in two completely different ciphertexts.

3. Vault Encapsulation & Masking
Obfuscation: Original filenames and extensions are stripped and replaced with a Randomized UUID.

Storage: All assets are encapsulated into .vault files within the local /vault directory.

Metadata Privacy: Without the Master Password, an observer cannot determine what type of file (PDF, Source Code, Image) is being stored.

```
<h2> [!CAUTION] </h2>

<h2> ⚠️ Important Security Notice: Zero-Recovery Policy </h2>
Zero-Trust means Zero-Recovery. <h4> * COMRADE does not store your password, hashes, or "backdoors" in any local database or cloud server</h4>

If you lose your Master Password, the data inside the vault becomes mathematically impossible to recover. <h4> * There is no "Forgot Password" mechanism. Please secure your Master Password in a physical location </h4>
