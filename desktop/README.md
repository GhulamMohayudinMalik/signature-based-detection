# 🛡️ MalGuard Desktop CLI

**Signature-Based Malware Detection System - Command Line Interface**

A powerful, cross-platform malware scanner using SHA-256 hash signatures, YARA rules, and quarantine management.

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Commands](#-commands)
- [Module Details](#-module-details)
- [Configuration](#-configuration)
- [Sample Data](#-sample-data)
- [Testing](#-testing)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **SHA-256 Matching** | Fast signature-based malware detection |
| **YARA Rules** | Advanced pattern matching (optional) |
| **HMAC Protection** | Tamper-proof signature database |
| **Cross-Platform** | Windows, macOS, Linux support |
| **Import/Export** | Share signature databases |
| **Scan Logging** | Track all scans in JSONL format |
| **Colored Output** | Red for threats, green for clean |
| **JSON Mode** | Machine-readable output for automation |
| **Quarantine** | Safely isolate detected files |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     MalGuard Desktop CLI                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   main.py    │───▶│   Scanner    │───▶│   Results    │  │
│  │  (CLI Entry) │    │   Engine     │    │   Output     │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                   │          │
│         ▼                   ▼                   ▼          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Colors     │    │   FileHasher │    │  Quarantine  │  │
│  │  (colorama)  │    │   (SHA-256)  │    │   Manager    │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                             │                              │
│         ┌───────────────────┼───────────────────┐          │
│         ▼                   ▼                   ▼          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Signature   │    │    YARA      │    │    Scan      │  │
│  │   Database   │    │   Engine     │    │   Logger     │  │
│  │ (HMAC-SHA256)│    │  (Optional)  │    │   (JSONL)    │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Installation

### Requirements
- Python 3.8 or higher
- pip (Python package manager)

### Steps

```bash
# 1. Navigate to desktop directory
cd desktop

# 2. Install dependencies
pip install -r requirements.txt

# 3. Verify installation
python main.py --help
```

### Dependencies

| Package | Purpose | Required |
|---------|---------|----------|
| `colorama` | Colored terminal output | Yes |
| `yara-python` | YARA rule support | Optional |

---

## 🚀 Quick Start

```bash
# Import sample malware signatures (25 signatures)
python main.py import ../data/sample_signatures.json

# Verify signatures loaded
python main.py list

# Scan a file
python main.py scan suspicious_file.exe

# Scan with JSON output (for automation)
python main.py scan file.exe --json

# Scan entire directory
python main.py scan C:\Downloads --all

# View quarantine
python main.py quarantine list

# View statistics
python main.py stats
```

---

## 📝 Commands

### `scan` - Scan Files or Directories

```bash
# Scan single file (executables only)
python main.py scan file.exe

# Scan all file types
python main.py scan file.txt --all

# Output as JSON (for scripting)
python main.py scan file.exe --json
python main.py scan file.exe -j

# Scan directory with all files, JSON output
python main.py scan C:\Downloads --all --json
```

**Flags:**
| Flag | Short | Description |
|------|-------|-------------|
| `--all` | `-a` | Scan all file types |
| `--json` | `-j` | Output results as JSON |

**Exit Codes:**
| Code | Meaning |
|------|---------|
| 0 | Success / Clean |
| 1 | Error |
| 2 | Malware Detected |

---

### `add` - Add Malware Signature

```bash
# Add signature with default severity (medium)
python main.py add malware.exe "Trojan.Generic"

# Add with specific severity
python main.py add ransomware.exe "Ransomware.Locky" --severity critical
python main.py add adware.exe "Adware.Genieo" -s low
```

**Severity Levels:** `low`, `medium`, `high`, `critical`

---

### `remove` - Remove Signature

```bash
python main.py remove <sha256-hash>
```

---

### `list` - List All Signatures

```bash
python main.py list
```

---

### `import` - Import Signatures

```bash
python main.py import signatures.json
python main.py import ../data/sample_signatures.json
```

---

### `export` - Export Signatures

```bash
python main.py export my_signatures.json
```

---

### `history` - Detection History

```bash
python main.py history
```

---

### `stats` - Scanning Statistics

```bash
python main.py stats
```

---

### `quarantine` - Manage Quarantined Files

The quarantine feature safely isolates detected malware files.

```bash
# List all quarantined files
python main.py quarantine list

# Restore a file (by hash or partial hash)
python main.py quarantine restore abc123
python main.py quarantine restore abc123 --to /path/to/restore

# Permanently delete a quarantined file
python main.py quarantine delete abc123

# Clear all quarantined files
python main.py quarantine clear
```

**Subcommands:**
| Command | Description |
|---------|-------------|
| `list` | Show all quarantined files with metadata |
| `restore <hash>` | Restore file to original location |
| `restore <hash> --to <path>` | Restore to specific location |
| `delete <hash>` | Permanently delete quarantined file |
| `clear` | Delete all quarantined files |

---

## 🎨 Output Modes

### Standard Output (with colors)
```
🔍 Scanning file: suspicious.exe
--------------------------------------------------
🚨 MALWARE DETECTED!
   File:     suspicious.exe
   Malware:  Trojan.Generic    (red)
   Severity: critical          (red + bold)
   SHA-256:  abc123...         (dim)
```

### JSON Output (`--json`)
```json
{
  "file_name": "suspicious.exe",
  "file_size": 12345,
  "hash": "abc123...",
  "detected": true,
  "malware_name": "Trojan.Generic",
  "severity": "critical",
  "reason": "signature_match"
}
```

---

## 🔧 Module Details

### Directory Structure

```
desktop/
├── main.py                 # CLI entry point (~450 lines)
├── requirements.txt        # Dependencies
├── README.md              # This file
└── malguard/              # Core package
    ├── __init__.py        # Package exports
    ├── hasher.py          # SHA-256 hashing
    ├── database.py        # Signature storage (HMAC)
    ├── scanner.py         # Scan engine
    ├── logger.py          # Scan logging
    ├── yara_engine.py     # YARA support (optional)
    ├── utils.py           # Utilities
    ├── colors.py          # Terminal colors (NEW)
    └── quarantine.py      # Quarantine manager (NEW)
```

### Module Responsibilities

| Module | Purpose |
|--------|---------|
| `hasher.py` | SHA-256 file hashing with chunked reading |
| `database.py` | HMAC-protected signature storage |
| `scanner.py` | Scan orchestration and results |
| `logger.py` | JSONL history logging |
| `yara_engine.py` | Optional YARA rule matching |
| `colors.py` | Cross-platform colored output |
| `quarantine.py` | File isolation and management |

---

## ⚙️ Configuration

### Config Directory Locations

| OS | Path |
|----|------|
| **Windows** | `%APPDATA%\malguard\` |
| **macOS** | `~/Library/Application Support/malguard/` |
| **Linux** | `~/.config/malguard/` |

### Config Files

| File | Purpose |
|------|---------|
| `signatures.json` | Malware signature database |
| `scan_log.jsonl` | Scan history |
| `quarantine/` | Quarantined files directory |
| `quarantine/manifest.json` | Quarantine metadata |
| `yara_rules/*.yar` | Optional YARA rules |

---

## 📊 Sample Data

### Pre-loaded Signatures (25)

Located at `../data/sample_signatures.json`:

| Category | Count | Examples |
|----------|-------|----------|
| **Trojans** | 6 | Zeus, Emotet, TrickBot |
| **Ransomware** | 5 | WannaCry, Locky, Petya, Ryuk |
| **Backdoors** | 3 | Gh0st, Mirai, Agent |
| **Worms** | 2 | Conficker, MyDoom |
| **Spyware** | 2 | Keylogger, Agent |
| **Adware** | 2 | BrowseFox, Genieo |
| **Test Files** | 3 | EICAR (MD5, SHA1, SHA256) |

### YARA Rules (8)

Located at `../data/yara_rules/malware_rules.yar`:
- EICAR_Test_File
- Suspicious_PowerShell_Commands
- Ransomware_File_Extensions
- Suspicious_Batch_Commands
- Generic_Malware_Strings
- Suspicious_Registry_Persistence
- Packed_Executable_Indicators
- Network_IOC_Patterns

---

## 🧪 Testing

### Test with EICAR

```bash
# Create EICAR test file
echo X5O!P%%@AP[4\PZX54(P^^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H* > eicar.txt

# Import signatures and scan
python main.py import ../data/sample_signatures.json
python main.py scan eicar.txt --all
```

### Test JSON Output

```bash
python main.py scan main.py --json | python -m json.tool
```

### Test Quarantine

```bash
python main.py quarantine list
python main.py quarantine clear
```

---

## 📄 License

MIT License

---

## 🔗 Related Components

- **Backend API** - REST server at `../backend/`
- **Web Frontend** - React app at `../web/`
- **Mobile App** - Expo app at `../mobile/`
