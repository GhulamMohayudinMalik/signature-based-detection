# MalGuard Desktop CLI - Usage Guide

A complete command-line malware detection system with signature-based scanning, YARA rules support, and quarantine management.

## Quick Start

```bash
cd desktop

# Install dependencies
pip install -r requirements.txt

# Scan a file for malware
python main.py scan path/to/file --all

# View help
python main.py --help
```

---

## Commands Reference

### 1. Scanning Files

```bash
# Scan a single file (executables only by default)
python main.py scan path/to/file

# Scan ALL file types (recommended)
python main.py scan path/to/file --all

# Scan entire directory recursively
python main.py scan path/to/directory --all

# Output results as JSON
python main.py scan path/to/file --all --json
```

**Features:**
- ✅ Signature-based hash matching (SHA-256)
- ✅ YARA rules detection
- ✅ ZIP archive scanning (extracts and scans contents)
- ✅ Nested archive support (up to 3 levels deep)
- ✅ Auto-quarantine for detected malware
- ✅ All results logged to history

**Exit Codes:**
- `0` = Clean (no malware found)
- `1` = Error (file not found, etc.)
- `2` = Malware detected

---

### 2. Signature Database Management

```bash
# List all signatures
python main.py list

# Add signature from a malware sample file
python main.py add path/to/malware.exe "Trojan.Generic" --severity high

# Remove a signature by hash
python main.py remove <sha256-hash>
```

**Severity Levels:** `low`, `medium`, `high`, `critical`

---

### 3. Import/Export Signatures

```bash
# Export all signatures to JSON
python main.py export signatures_backup.json

# Import signatures from JSON
python main.py import signatures_backup.json
```

**JSON Format:**
```json
{
  "signatures": {
    "sha256hash...": {
      "name": "Malware.Name",
      "severity": "high",
      "source": "manual"
    }
  }
}
```

---

### 4. Quarantine Management

When malware is detected, files are automatically moved to quarantine.

```bash
# List quarantined files
python main.py quarantine list

# Restore a file by exact filename
python main.py quarantine restore eicar.com

# Restore using partial hash
python main.py quarantine restore 275a021b

# Restore to custom location
python main.py quarantine restore eicar.com --to /path/to/restore/

# Permanently delete a quarantined file
python main.py quarantine delete eicar.com

# Clear all quarantined files
python main.py quarantine clear
```

**Quarantine Location:** `%APPDATA%\malguard\quarantine\` (Windows)

---

### 5. History & Statistics

```bash
# View recent detection history
python main.py history

# View scanning statistics
python main.py stats
```

**Example Stats Output:**
```
📊 Scanning Statistics
========================================
   Total scans:     25
   Detections:      5
   Clean files:     18
   Skipped files:   2
   Detection rate:  21.74%
========================================
```

---

## Configuration

**Config Directory:** `%APPDATA%\malguard\` (Windows) or `~/.config/malguard/` (Linux/Mac)

| File | Purpose |
|------|---------|
| `signatures.json` | Malware signature database |
| `scan_history.jsonl` | Scan history log |
| `quarantine/` | Isolated malware files |
| `quarantine/manifest.json` | Quarantine metadata |
| `yara_rules/` | Custom YARA rule files (*.yar) |

---

## YARA Rules

Place custom `.yar` or `.yara` files in the YARA rules directory:

```
%APPDATA%\malguard\yara_rules\
```

Example YARA rule:
```yara
rule EICAR_Test {
    meta:
        description = "EICAR Test File"
    strings:
        $eicar = "X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
    condition:
        $eicar
}
```

---

## Testing with EICAR

EICAR is a safe test file for antivirus testing.

1. Create a file with this exact content:
```
X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*
```

2. Save as `eicar.com` and scan:
```bash
python main.py scan eicar.com --all
```

**Expected Output:**
```
🚨 MALWARE DETECTED!
   File:     eicar.com
   Malware:  EICAR-Test-File-SHA256
   Severity: low
   SHA-256:  275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f
```

---

## Example Workflow

```bash
# 1. Seed the database with sample signatures
python main.py import sample_signatures.json

# 2. Scan a suspicious directory
python main.py scan ~/Downloads --all

# 3. Review what was quarantined
python main.py quarantine list

# 4. Restore a false positive
python main.py quarantine restore important_file.exe

# 5. Check statistics
python main.py stats

# 6. Export signatures for backup
python main.py export my_signatures.json
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "YARA not available" | Run `pip install yara-python` |
| ZIP scan errors | Windows Defender may block - add exclusion for test files |
| "Permission denied" | Run as administrator or check file permissions |
| File not found after scan | File was quarantined (check `python main.py quarantine list`) |

---

## Requirements

- Python 3.8+
- Optional: `yara-python` for YARA rules support

```bash
pip install -r requirements.txt
```

---

## Project Structure

```
desktop/
├── main.py              # CLI entry point
├── requirements.txt     # Dependencies
├── malguard/
│   ├── __init__.py      # Package exports
│   ├── scanner.py       # Core scanning logic
│   ├── database.py      # Signature database
│   ├── hasher.py        # SHA-256 hashing
│   ├── quarantine.py    # Quarantine management
│   ├── logger.py        # Scan history logging
│   ├── yara_engine.py   # YARA rules engine
│   ├── utils.py         # Utility functions
│   └── colors.py        # Terminal colors
└── malguard_tests/      # Test malware samples
```
