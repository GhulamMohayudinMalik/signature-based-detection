# MalGuard - Signature-Based Malware Detection System

## Project Overview

A cross-platform malware detection system using **hash-based signature matching** and **YARA rule analysis**.

### Platforms
| Platform | Technology | Status |
|----------|------------|--------|
| Desktop CLI | Python | 🔴 To Build |
| Web Backend | Python (FastAPI) | 🔴 To Build |
| Web Frontend | React + TypeScript | 🔴 To Build |
| Mobile App | React Native / Expo | 🔴 To Build |

---

## Core Functionality

### 1️⃣ Scanning Engine
- **Hash Calculation**: Compute SHA-256 hash of files
- **Signature Matching**: Compare hash against known malware database
- **YARA Rules**: Pattern-based behavioral detection
- **Extension Filtering**: Prioritize executable files (`.exe`, `.dll`, `.bat`, `.ps1`, `.jar`, etc.)

### 2️⃣ Signature Database
- **Storage**: Hash → `{malware_name, severity, added_date, source}`
- **Integrity**: HMAC-signed to prevent tampering
- **Operations**: Add, remove, search, import/export signatures
- **Sync**: Desktop ↔ Backend synchronization

### 3️⃣ Scanning Modes
- **Single File Scan**: Upload or select one file
- **Directory Scan**: Recursive folder scanning
- **Quick Scan**: Executables only
- **Full Scan**: All file types

### 4️⃣ Results & Reporting
- **Detection Details**: File path, hash, malware name, detection method
- **Scan History**: Timestamped log of all scans
- **Statistics**: Total scans, threats found, clean files

---

## Development Roadmap

### Phase 1: Desktop CLI (Core Foundation)
> Replicate and improve `desktop/main.py`

- [ ] **1.1** Project structure setup (`desktop/`)
- [ ] **1.2** Hash calculator module (SHA-256)
- [ ] **1.3** Signature database with HMAC integrity
- [ ] **1.4** File scanner with extension filtering
- [ ] **1.5** Directory recursive scanner
- [ ] **1.6** YARA rule integration (optional)
- [ ] **1.7** CLI interface with argparse
- [ ] **1.8** Scan logging (JSONL format)
- [ ] **1.9** Cross-platform config paths

**Deliverable**: Working CLI tool that can scan files/folders and detect malware by hash

---

### Phase 2: Web Backend (API Server)
> FastAPI backend for web/mobile clients

- [ ] **2.1** Project structure setup (`backend/`)
- [ ] **2.2** FastAPI application scaffold
- [ ] **2.3** SQLite/PostgreSQL signature database
- [ ] **2.4** File upload & scan endpoint
- [ ] **2.5** Hash-only scan endpoint
- [ ] **2.6** Signature CRUD endpoints
- [ ] **2.7** Scan history endpoints
- [ ] **2.8** Statistics/dashboard endpoint
- [ ] **2.9** CORS configuration for web/mobile

**Deliverable**: REST API that web and mobile apps can use

---

### Phase 3: Web Frontend (React App)
> Modern UI for browser-based scanning

- [ ] **3.1** Vite + React + TypeScript setup
- [ ] **3.2** API client service
- [ ] **3.3** File upload with drag-drop
- [ ] **3.4** Real-time scan progress
- [ ] **3.5** Scan results display
- [ ] **3.6** Signature database viewer
- [ ] **3.7** Scan history page
- [ ] **3.8** Dashboard with statistics
- [ ] **3.9** Dark/light theme

**Deliverable**: Web app connected to backend for file scanning

---

### Phase 4: Mobile App (React Native)
> Mobile client using shared backend

- [ ] **4.1** Expo / React Native setup
- [ ] **4.2** File picker integration
- [ ] **4.3** Scan results screen
- [ ] **4.4** History screen
- [ ] **4.5** Push notifications for detections

**Deliverable**: Mobile app for on-the-go file scanning

---

## Future Enhancements (After Core)

| Feature | Description | Priority |
|---------|-------------|----------|
| **Real-Time Protection** | File system watcher daemon | Medium |
| **Quarantine System** | Move threats to secure folder | Medium |
| **VirusTotal API** | Cloud verification for unknown files | Low |
| **Scheduled Scans** | Cron-based periodic scanning | Low |
| **Multi-Hash Support** | MD5 + SHA-1 + SHA-256 | Low |
| **Electron Desktop GUI** | Cross-platform desktop app with UI | Low |
| **Signature Updates** | Auto-download new signatures | Medium |

---

## Project Structure (Target)

```
signaturebasedetection-main/
├── project.md              # This file
├── desktop/                # Desktop CLI Application
│   ├── main.py            # Entry point
│   ├── scanner/           # Scanning engine
│   ├── database/          # Signature DB
│   └── utils/             # Helpers
├── backend/               # Web API Server
│   ├── main.py           # FastAPI app
│   ├── routes/           # API endpoints
│   ├── models/           # Data models
│   ├── services/         # Business logic
│   └── data/             # Signatures, YARA rules
├── web/                   # React Web Frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/     # API client
│   │   └── lib/
│   └── package.json
└── mobile/                # React Native Mobile App
    ├── src/
    └── app.json
```

---

## Getting Started

**Next Step**: Begin with **Phase 1.1** - Set up desktop CLI project structure

```bash
# We will start here
cd desktop/
python main.py --help
```
