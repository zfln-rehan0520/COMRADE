<div align="center">
<h1>🛡️ COMRADE: A Brother That Gaurds Your Data 🛡️ </h1>

<h4>Cyber Operations Module for Resilient Authentication and Data Encryption</h4>

![Version](https://img.shields.io/badge/version-1.0.2-ff8c00)
![License](https://img.shields.io/badge/license-MIT-white)
![Security](https://img.shields.io/badge/encryption-AES--256--GCM-00ffff)
![Platform](https://img.shields.io/badge/platform-CLI/GUI-blue)

<h6>COMRADE is a high-security, local-first encryption engine designed for developers and privacy advocates. It ensures that sensitive documents, source code, and private data are mathematically protected via industry-standard cryptographic protocols, ensuring your data remains yours alone</h6>

</div>

----------------------------------------------------------------------------------------------------------------------------

## 🛠️ Core Features

* **Zero-Knowledge Architecture**: Encryption and decryption occur locally. Your Master Key is never stored.
* **Kernel Stealth (Ghost Mode)**: Utilizes `SetFileAttributesW` to flag the vault as a **System Protected** component, making it invisible even if "Show Hidden Files" is enabled.
* **Anti-Forensic Wiping**: Assets are overwritten with random bits (`os.urandom`) before deletion to prevent data recovery.
* **Operational Integrity**: Employs a file-handle lock to prevent accidental deletion of the vault while the application is active.
* **Hybrid Interface**: Full support for both a high-contrast CLI and a modern GUI (CustomTkinter).

---
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
**OS**: Windows 10/11 (Required for Stealth/Locking features).
* **Python**: 3.10 or higher.

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
Secure a File :- python main.py --secure "path/to/file.txt"
Extract Asset :- python main.py --extract <VAULT_ID>.vault
Secure Wipe :-  python main.py --remove  <VAULT_ID>.vault

```
[!NOTE]
When securing a file, the original remains untouched for safety. We recommend manually deleting the source file only after verifying the encryption.
----------------------------------------------------------------------------------------------------------------------------
Graphical User Interface (GUI)
For a visual dashboard experience, launch the application without flags:

```powershell
python main.py
```
---
🛠️ 1. Enable System Protection (To Hide the Vault)
Windows has a "Master Switch" that hides critical OS files. You want this checked so your vault disappears from standard view.

Open File Explorer and click the three dots (...) or View > Options.

Navigate to the View tab.

Scroll down to "Hide protected operating system files (Recommended)".

CHECK this box. 5.  Click Apply.

Effect: The vault/ folder will now be physically invisible even if "Show Hidden Files" is turned on.

🛠️ 2. Disable the Master Switch (To See/Debug the Vault)
If you need to physically see the encrypted blobs or the manifest for debugging, you must temporarily reverse the setting.

In the same View tab, UNCHECK "Hide protected operating system files (Recommended)".

Windows will show a warning: "You have chosen to display protected operating system files..." Click Yes.

CHECK "Show hidden files, folders, and drives".

Effect: The vault/ folder and its contents will appear as faded/semi-transparent icons, indicating they are in "Ghost Mode."
---
```powershell
Path                           Visibility        Status         Purpose
----                           ----------        ------         -------
COMRADE/main.py                 Visible          Active        Main Bootloader
COMRADE/core/                   Visible          Active       Encryption & File Logic
COMRADE/cli/                    Visible          Active       Banner & Terminal Interface
COMRADE/vault/                  Ghosted         Secured       Secured Root Directory
COMRADE/vault/.vault_manifest   Ghosted         Secured       Encrypted Metadata Mapping
COMRADE/vault/*.vault           Ghosted         Secured       Encrypted Data Blobs
```
---

<h2>🔒 Security Architecture</h2>

COMRADE is engineered on a Zero-Knowledge and Local-First philosophy. The architecture ensures that the application never possesses the means to decrypt your data without your active input.
```powershell
Security Architecture

1. Key Derivation
COMRADE does not use the master password directly as an encryption key.
Using PBKDF2 with a unique cryptographic salt, the password is transformed into a high-entropy 256-bit encryption key, strengthening resistance against brute-force and dictionary attacks.

2. Authenticated Encryption
COMRADE uses AES-256-GCM, providing both confidentiality and integrity.

Confidentiality: Data is protected using AES-256 encryption.
Integrity Protection: Authentication tags detect any tampering or modification.
Nonce-Based Security: A unique nonce is generated for every encryption session, ensuring identical files produce different ciphertexts.

3. Vault Encapsulation
Encrypted data is stored as isolated .vault containers inside the local vault.

Original filenames are replaced with randomized identifiers.
Data remains encapsulated within encrypted vault files.
Without the master password, file contents and metadata remain concealed.

```
🛠️ The PowerShell "Wipe" Commands
```powershell
# 1. Force delete the vault and all contents
Remove-Item -Path vault -Recurse -Force

# 2. Force delete all project folders and the virtual environment
Remove-Item -Path core, cli, ui, assets, venv -Recurse -Force

# 3. Delete the individual files
# (Note: In PowerShell, use commas to separate multiple files)
Remove-Item -Path main.py, requirements.txt, README.md, .gitignore -Force
```
<h4>🧹 Final Step
Once those commands finish, your COMRADE folder will be empty. You can move up and delete the root folder:</h4>

```powershell
cd ..
Remove-Item -Path COMRADE -Recurse -Force
```

<h2> [ ! CAUTION ! ] </h2>

<h2> ⚠️ Important Security Notice: Zero-Recovery Policy </h2>
Zero-Trust means Zero-Recovery. <h4> * COMRADE does not store your password, hashes, or "backdoors" in any local database or cloud server</h4>

If you lose your Master Password, the data inside the vault becomes mathematically impossible to recover. <h4> * There is no "Forgot Password" mechanism. Please secure your Master Password in a physical location </h4>
