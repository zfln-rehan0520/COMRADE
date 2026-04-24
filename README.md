# 🛡️ COMRADE: Zero-Trust Local Vault

**COMRADE** is a local-first, high-security file encryption tool designed for privacy-conscious users. It utilizes industry-standard authenticated encryption to ensure your data is not only locked but also protected from tampering.

## 🚀 Features
- **Zero-Trust Architecture:** 100% local. No servers, no leaks.
- **Dual Interface:** Powerful CLI for automation and a modern GUI for daily use.
- **Military-Grade Crypto:** - **AES-256 (GCM Mode)** for authenticated encryption.
  - **PBKDF2** with 100,000 iterations for secure key derivation.
- **Stealth Vault:** Files are renamed to random hex strings to hide file types and metadata.

## 🛠️ Tech Stack
- **Language:** Python 3.x
- **Crypto:** `cryptography` library
- **UI:** `customtkinter` (Modern Dark Mode)
- **CLI:** `rich` for formatted terminal output

## 📦 Installation
1. Clone the repository:
   `git clone https://github.com/your-username/COMRADE.git`
2. Install dependencies:
   `pip install -r requirements.txt`

## 🕹️ Usage
### CLI Mode
- **Secure a file:** `python main.py --secure my_data.pdf`
- **List vault:** `python main.py --list`

### GUI Mode
Simply run the application without arguments:
`python main.py`

## 🏗️ Project Structure
- `core/`: Cryptographic engine and file management.
- `ui/`: Modern desktop interface logic.
- `cli/`: Terminal interface logic.
- `vault/`: Your encrypted "Safe Zone" (Git Ignored).
