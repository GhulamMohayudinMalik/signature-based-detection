# 🛡️ MalGuard - Signature-Based Malware Detection System

A comprehensive, cross-platform malware detection system using SHA-256 hash signatures and YARA rules.

## 📁 Project Structure

```
MalGuard/
├── desktop/          # Command-Line Interface (Python)
├── backend/          # REST API Server (FastAPI)
├── web/              # Web Frontend (React + TypeScript)
├── mobile/           # Mobile App (Expo React Native)
└── data/             # Sample signatures and YARA rules
```

## 🚀 Quick Start

### 1. Desktop CLI
```bash
cd desktop
python main.py scan <path>           # Scan file or directory
python main.py import ../data/sample_signatures.json  # Load sample signatures
python main.py list                  # List all signatures
```

### 2. Backend API
```bash
cd backend
.\venv\Scripts\activate              # Windows
uvicorn main:app --reload --host 0.0.0.0
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### 3. Web Frontend
```bash
cd web
npm install
npm run dev
# Visit: http://localhost:5173
```

### 4. Mobile App
```bash
cd mobile
npm install
npx expo start
# Scan QR with Expo Go app
```

## ✨ Features

### Core Detection
- **SHA-256 Hash Matching** - Fast signature-based detection
- **YARA Rules** - Advanced pattern matching (optional)
- **Extension Filtering** - Focus on executable files
- **HMAC Database** - Tamper-protected signature storage

### Desktop CLI Commands
| Command | Description |
|---------|-------------|
| `scan <path>` | Scan file or directory |
| `scan <path> --all` | Scan ALL file types |
| `add <file> <name>` | Add malware signature |
| `remove <hash>` | Remove signature |
| `list` | List all signatures |
| `import <file>` | Import signatures from JSON |
| `export <file>` | Export signatures to JSON |
| `history` | View detection history |
| `stats` | View scan statistics |

### API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/scan/file` | Upload and scan file |
| POST | `/scan/files` | Batch file scan |
| POST | `/scan/hash` | Check hash lookup |
| GET/POST/DELETE | `/signatures` | Signature CRUD |
| GET | `/history` | Scan history |
| GET | `/stats` | Dashboard stats |

## 📊 Sample Data

### Pre-loaded Signatures (25)
Located in `data/sample_signatures.json`:
- EICAR test file (standard AV test)
- Trojans (Zeus, Emotet, TrickBot)
- Ransomware (WannaCry, Locky, Petya)
- Worms (Conficker, MyDoom)
- Spyware, Adware, PUPs

### YARA Rules (8)
Located in `data/yara_rules/malware_rules.yar`:
- EICAR test file detection
- Suspicious PowerShell commands
- Ransomware file extensions
- Registry persistence patterns
- Network IOC patterns
- Packed executable indicators

## 🧪 Testing with EICAR

The EICAR test file is a standard antivirus test:
```bash
# Create EICAR test file
echo 'X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*' > eicar.txt

# Scan it
python main.py import ../data/sample_signatures.json
python main.py scan eicar.txt --all
# Should detect: EICAR-Test-File
```

## 🔧 Requirements

- **Python 3.8+** (Desktop & Backend)
- **Node.js 18+** (Web & Mobile)
- **yara-python** (Optional - for YARA rules)

## 📄 License

MIT License - See LICENSE file

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request
