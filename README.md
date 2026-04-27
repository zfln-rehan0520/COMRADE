<div align="center">
  <br />
  <h1>🛡️ COMRADE 🛡️</h1>
  <strong>Cyber Operations Module for Resilient Authentication and Data Encryption</strong>
  <br /><br />
  
  ![Version](https://img.shields.io/badge/version-1.0.2-ff8c00?style=for-the-badge)
  ![License](https://img.shields.io/badge/license-MIT-white?style=for-the-badge)
   ![Python](https://img.shields.io/badge/python-3.12+-blue?style=for-the-badge&logo=python)
  ![Security](https://img.shields.io/badge/encryption-AES--256--GCM-00ffff?style=for-the-badge)
  ![Platform](https://img.shields.io/badge/platform-Cross--Platform-blue?style=for-the-badge)

  <p align="center">
    COMRADE is a high-security, local-first encryption engine engineered for developers and privacy advocates. 
    By leveraging industry-standard cryptographic protocols and OS-level stealth techniques, 
    COMRADE ensures your sensitive assets remain mathematically inaccessible to unauthorized entities.
  </p>
</div>

---

## 🛠️ Core Features

* **Zero-Knowledge Architecture**: Encryption and decryption occur locally in memory. Your Master Key is never cached or stored on disk.
* **Kernel Stealth (Ghost Mode)**: On Windows, utilizes `SetFileAttributesW` to flag the vault as a **System Protected** component—invisible even if "Show Hidden Files" is enabled.
* **Anti-Forensic Wiping**: Implements a secure-erase protocol where assets are overwritten with high-entropy random bits (`os.urandom`) before physical deletion.
* **Operational Integrity**: Employs a kernel-level file-handle lock to prevent accidental or malicious deletion of the vault while the application is active.

---


## 🛠️ Project Structure
```text
COMRADE/
├── .gitignore               # Multi-platform exclusion rules
├── README.md                # Documentation
├── requirements.txt         # Global dependencies
├── main.py                  # Entry point & Cross-platform lock logic
├── core/                    # Logic Layer
│   ├── encryption.py        # AES-256-GCM engine
│   ├── file_manager.py      # Stealth & Wipe logic
│   └── auth.py              # Scrypt KDF logic
├── cli/                     # Interface Layer
└── ui/                      # Dashboard Layer
├── .env.example            # Template for local configuration
```
-----

## 🌍 Multi-Platform Deployment & Usage

COMRADE is engineered to adapt its security layer based on the host Operating System.

### 1. Environment Setup

## Windows Powershell {structured}
| Task | Windows 10/11 (powershell) |
| :--- | :--- |
| **Clone** | `git clone https://github.com/zfln-rehan0520/COMRADE.git` |
| **Chanage Directory** | `cd COMRADE` |
| **Install Venv** | `py -m venv venv` |
| **Policy Bypass** | `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` |
| **Activate** | `.\venv\Scripts\Activate.ps1` |
| **Install Req** | `pip install -r requirements.txt` |
| **Install Colorama** | `pip install colorama` |



## Linux cmd line {structured}

| Task | Linux / macOS (Terminal) |
| :--- | :--- |
| **Clone** | `git clone https://github.com/zfln-rehan0520/COMRADE.git` |
| **Chanage Directory** | `cd COMRADE` |
| **Python req** | `sudo apt install python3 python3-pip` |
| **Install Venv** | `sudo apt install python3-venv` |
| **Set-up Venv** | `python3 -m venv venv` |
| **Activate** | `source venv/bin/activate` |
| **Install Req** | `pip install -r requirements.txt` |
| **Install Colorama** | `pip install colorama` |
| **Install Tkinter** | `sudo apt install python3-tk` |
| **Set-up Tkinter** | `python3 -m tkinter` |

```text

# High-speed setup for Debian/Ubuntu/Kali
git clone https://github.com/zfln-rehan0520/COMRADE.git && cd COMRADE && sudo apt install -y python3-tk python3-venv && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt colorama

```

### 2. Operational Commands
Once the environment is active, use the following commands:

* **List Vault Content**: `python main.py --list`
* **Secure a File**: `python main.py --secure "path/to/file.txt"`
* **Extract Asset**: `python main.py --extract <VAULT_ID>.vault`
* **Secure Wipe**: `python main.py --remove <VAULT_ID>.vault`
* **Launch GUI**: `python main.py`

### 3. OS-Specific Security Logic

* **Windows**: Uses Kernel-level attribute flags (System + Hidden) and persistent file handles for locking.
* **Linux/macOS**: Utilizes the dot-prefix (`.comrade_vault`) for directory stealth and `fcntl` advisory locking to maintain operational integrity.
* **GUI Support**: Linux users may require `sudo apt install python3-tk` for GUI rendering.

---
🔒 SECURITY ARCHITECTURE - COMRADE
----------------------------------
COMRADE implements a "Defense-in-Depth" strategy, ensuring that even if the 
host machine is compromised, the encrypted assets remain computationally 
infeasible to decrypt.

```text
1. KEY DERIVATION & MEMORY HARDNESS

   - KDF: Scrypt-based Key Derivation Function.
   
   - Parameters: Configured with high N, r, p work factors to maximize 
     memory hardness, rendering GPU/ASIC brute-force attacks unviable.
     
   - Salt: Unique 16-byte high-entropy salt per vault (via os.urandom), 
     mitigating rainbow table attacks.
     
   - Zero-Persistence: Derived keys reside strictly in volatile memory; 
     never persisted to swap space or disk.

2. AUTHENTICATED ENCRYPTION (AEAD)

   - Protocol: AES-256-GCM (Galois/Counter Mode).
   
   - Confidentiality: Industry-standard 256-bit symmetric encryption.
   
   - Integrity: GHASH Authentication Tags detect bit-level tampering. 
     Decryption aborts if the tag is invalid (Anti-Tamper).
     
   - Nonce Isolation: Unique 96-bit Initialization Vector (IV) per 
     encryption cycle to ensure ciphertext divergence.

3. ANTI-FORENSIC & OPERATIONAL LOGIC

   - Secure Wipe: Implements high-entropy random bit overwriting 
     before file deletion to defeat disk recovery tools.
     
   - Atomic Writes: Utilizes write-and-rename patterns to prevent 
     data corruption during unexpected power loss.

   ```

---
