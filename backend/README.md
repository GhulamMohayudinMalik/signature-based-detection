# 🛡️ MalGuard Backend API

**Signature-Based Malware Detection System - REST API Server**

A FastAPI-powered backend providing malware scanning, signature management, quarantine, and scan history via RESTful endpoints.

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [API Endpoints](#-api-endpoints)
- [Database Schema](#-database-schema)
- [Configuration](#-configuration)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **RESTful API** | Clean, documented endpoints |
| **File Upload Scanning** | Single and batch file upload |
| **Hash Lookup** | Quick signature check without upload |
| **Signature CRUD** | Full management of malware signatures |
| **Bulk Import/Export** | JSON file import and export |
| **Quarantine Management** | Track and manage isolated files |
| **Scan History** | Track all scanning activity |
| **Search & Filter** | Find signatures by name or severity |
| **Auto Documentation** | Swagger UI & ReDoc |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     MalGuard Backend API                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    FastAPI Application                   │   │
│  │  Routes: /signatures, /scan, /history, /quarantine       │   │
│  └─────────────────────────────────────────────────────────┘   │
│         │                                                       │
│  ┌──────┴──────────────────────────────────────────────────┐   │
│  │                         Routes                           │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────┐    │   │
│  │  │ /scan   │ │/signat- │ │/history │ │ /quarantine │    │   │
│  │  │         │ │ ures    │ │ /stats  │ │             │    │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────────┘    │   │
│  └─────────────────────────────────────────────────────────┘   │
│         │                                                       │
│  ┌──────┴──────────────────────────────────────────────────┐   │
│  │              Services: database.py, scanner.py           │   │
│  └──────┬──────────────────────────────────────────────────┘   │
│         │                                                       │
│  ┌──────┴──────────────────────────────────────────────────┐   │
│  │                   data/malguard.db                       │   │
│  │  Tables: signatures, scan_history                        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 Installation

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

---

## 🚀 Quick Start

```bash
# Start server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Seed with sample signatures
curl -X POST http://localhost:8000/seed

# API Docs
http://localhost:8000/docs
```

---

## 📡 API Endpoints

### Overview

| Category | Endpoints |
|----------|-----------|
| **System** | `GET /`, `GET /health`, `GET /info`, `POST /seed` |
| **Scanning** | `POST /scan/file`, `/scan/files`, `/scan/hash` |
| **Signatures** | `GET/POST/DELETE /signatures`, search, filter, bulk |
| **History** | `GET/DELETE /history`, `GET /stats` |
| **Quarantine** | `GET/POST/DELETE /quarantine` |

---

### 🔧 System Endpoints

#### GET `/health`
Health check with database status.
```json
{"status": "healthy", "database": "connected", "signatures": 25}
```

#### GET `/info`
System information with features and stats.
```json
{
  "name": "MalGuard Backend API",
  "version": "1.0.0",
  "features": {"signature_matching": true, "yara_rules": true, ...},
  "endpoints": {...}
}
```

#### POST `/seed`
Load sample signatures from `data/sample_signatures.json`.
```json
{"success": true, "message": "Database seeded: 25 added"}
```

---

### 🔍 Scan Endpoints

#### POST `/scan/file`
Upload and scan a single file.
```bash
curl -X POST http://localhost:8000/scan/file -F "file=@suspicious.exe"
```

#### POST `/scan/files`
Upload and scan multiple files.
```bash
curl -X POST http://localhost:8000/scan/files -F "files=@file1.exe" -F "files=@file2.dll"
```

#### POST `/scan/hash`
Check if a hash exists in the database.
```bash
curl -X POST http://localhost:8000/scan/hash -H "Content-Type: application/json" \
  -d '{"hash": "44d88612fea8a8f36de82e1278abb02f"}'
```

---

### 🗄️ Signature Endpoints

#### GET `/signatures`
List all signatures with pagination.
```bash
curl "http://localhost:8000/signatures?limit=10&offset=0"
```

#### GET `/signatures/search?q=`
Search signatures by name or hash.
```bash
curl "http://localhost:8000/signatures/search?q=trojan"
```

#### GET `/signatures/filter/severity/{level}`
Filter by severity: `low`, `medium`, `high`, `critical`.
```bash
curl "http://localhost:8000/signatures/filter/severity/critical"
```

#### POST `/signatures`
Add a new signature.
```bash
curl -X POST http://localhost:8000/signatures \
  -H "Content-Type: application/json" \
  -d '{"hash": "abc...", "name": "Trojan.Generic", "severity": "high"}'
```

#### POST `/signatures/bulk`
Import multiple signatures at once.
```bash
curl -X POST http://localhost:8000/signatures/bulk \
  -H "Content-Type: application/json" \
  -d '[{"hash": "...", "name": "..."}, ...]'
```

#### POST `/signatures/import-json`
Upload a JSON file with signatures.
```bash
curl -X POST http://localhost:8000/signatures/import-json -F "file=@signatures.json"
```

#### GET `/signatures/export`
Export all signatures as downloadable JSON.
```bash
curl http://localhost:8000/signatures/export -o signatures_backup.json
```

#### DELETE `/signatures/{hash}`
Remove a specific signature.

#### DELETE `/signatures/all`
Clear all signatures.

---

### 📋 History Endpoints

#### GET `/history`
Get scan history.
```bash
curl "http://localhost:8000/history?limit=100&detections_only=true"
```

#### DELETE `/history`
Clear all scan history.

#### GET `/stats`
Get dashboard statistics.
```json
{
  "total_signatures": 25,
  "total_scans": 150,
  "total_detections": 3,
  "recent_detections": [...]
}
```

---

### 🔒 Quarantine Endpoints

#### GET `/quarantine`
List all quarantined files.
```json
{
  "total": 2,
  "files": [
    {"hash": "abc...", "original_name": "malware.exe", "malware_name": "Trojan.Generic", ...}
  ]
}
```

#### GET `/quarantine/{hash}`
Get details of a specific quarantined file.

#### POST `/quarantine`
Add a file to quarantine tracking.
```bash
curl -X POST "http://localhost:8000/quarantine?file_hash=abc&original_name=file.exe&malware_name=Trojan"
```

#### POST `/quarantine/{hash}/restore`
Restore a quarantined file.
```bash
curl -X POST "http://localhost:8000/quarantine/abc123/restore"
```

#### DELETE `/quarantine/{hash}`
Remove a file from quarantine (and delete if exists).

#### DELETE `/quarantine`
Clear all quarantine records.

#### GET `/quarantine/stats/count`
Get count of quarantined files.

---

## 🗃️ Database Schema

### `signatures` table
| Column | Type | Description |
|--------|------|-------------|
| `hash` | TEXT PK | SHA-256 hash |
| `name` | TEXT | Malware name |
| `severity` | TEXT | low/medium/high/critical |
| `source` | TEXT | Origin |
| `added_on` | TIMESTAMP | Creation time |

### `scan_history` table
| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | Auto ID |
| `file_name` | TEXT | Scanned file |
| `hash` | TEXT | SHA-256 |
| `detected` | INTEGER | 0=clean, 1=detected |
| `malware_name` | TEXT | Name if detected |
| `timestamp` | TIMESTAMP | Scan time |

---

## ⚙️ Configuration

Edit `config.py`:
```python
DATABASE_PATH = "data/malguard.db"
CORS_ORIGINS = ["http://localhost:3000", "http://localhost:5173"]
MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB
```

---

## 📁 Project Structure

```
backend/
├── main.py              # FastAPI app
├── config.py            # Settings
├── models.py            # Pydantic schemas
├── database.py          # SQLite service
├── scanner.py           # Scanning service
├── requirements.txt
├── README.md
├── data/
│   ├── malguard.db     # SQLite database
│   └── quarantine/     # Quarantined files
└── routes/
    ├── __init__.py
    ├── signatures.py   # Signature CRUD
    ├── scan.py         # File scanning
    ├── history.py      # History & stats
    └── quarantine.py   # Quarantine management (NEW)
```

---

## 🔗 Related

- **Desktop CLI** - `../desktop/`
- **Web Frontend** - `../web/`
- **Mobile App** - `../mobile/`
