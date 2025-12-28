# MalGuard Backend API - Usage Guide

A FastAPI-based malware detection backend providing REST API endpoints for signature-based scanning, YARA rules detection, and quarantine management.

## Quick Start

```bash
cd backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload

# API docs available at:
# http://localhost:8000/docs
```

---

## API Endpoints Reference

### Health & Status

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Server health check |
| GET | `/stats` | Scanning statistics |
| POST | `/seed` | Seed database with sample signatures |

```bash
# Check server status
curl http://localhost:8000/health

# Get statistics
curl http://localhost:8000/stats
```

---

### File Scanning

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/scan/file` | Scan single file |
| POST | `/scan/files` | Scan multiple files |

**Features:**
- ✅ SHA-256 signature matching
- ✅ YARA rules detection
- ✅ ZIP archive extraction and scanning
- ✅ Nested archive support (up to 3 levels)
- ✅ Auto-quarantine for detections
- ✅ All results logged to history

```bash
# Scan a single file
curl -X POST -F "file=@malware.exe" \
  "http://localhost:8000/scan/file?scan_all=true"

# Scan multiple files
curl -X POST -F "files=@file1.exe" -F "files=@file2.dll" \
  "http://localhost:8000/scan/files?scan_all=true"
```

**Query Parameters:**
- `scan_all=true` - Scan all file types (not just executables)

**Response Example:**
```json
{
  "results": [
    {
      "file_name": "eicar.com",
      "file_size": 68,
      "hash": "275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f",
      "detected": true,
      "malware_name": "EICAR-Test-File-SHA256",
      "severity": "low",
      "reason": "signature_match"
    }
  ],
  "total": 1,
  "detected": 1,
  "clean": 0
}
```

---

### Signature Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/signatures` | List all signatures |
| GET | `/signatures/{hash}` | Get specific signature |
| POST | `/signatures` | Add new signature |
| DELETE | `/signatures/{hash}` | Remove signature |
| GET | `/signatures/search?q=` | Search signatures |
| GET | `/signatures/filter/severity/{level}` | Filter by severity |

```bash
# List all signatures
curl http://localhost:8000/signatures

# Add a signature
curl -X POST http://localhost:8000/signatures \
  -H "Content-Type: application/json" \
  -d '{"hash": "abc123...", "name": "Trojan.Generic", "severity": "high"}'

# Search signatures
curl "http://localhost:8000/signatures/search?q=eicar"

# Filter by severity
curl http://localhost:8000/signatures/filter/severity/critical
```

---

### Import/Export Signatures

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/signatures/export` | Export all signatures as JSON |
| POST | `/signatures/import-json` | Import from JSON file |
| POST | `/signatures/bulk` | Bulk add signatures |

```bash
# Export signatures
curl http://localhost:8000/signatures/export -o signatures.json

# Import signatures
curl -X POST -F "file=@signatures.json" \
  http://localhost:8000/signatures/import-json
```

---

### Scan History

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/history` | Get scan history |
| DELETE | `/history` | Clear history |

```bash
# Get last 50 scans
curl "http://localhost:8000/history?limit=50"

# Get only detections
curl "http://localhost:8000/history?detected_only=true"
```

---

### Quarantine Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/quarantine` | List quarantined files |
| POST | `/quarantine/{hash}/restore` | Restore a file |
| DELETE | `/quarantine/{hash}` | Delete quarantined file |
| DELETE | `/quarantine` | Clear all quarantine |

```bash
# List quarantined files
curl http://localhost:8000/quarantine

# Delete a quarantined file
curl -X DELETE http://localhost:8000/quarantine/275a021b...

# Clear all
curl -X DELETE http://localhost:8000/quarantine
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_PATH` | `./data/malguard.db` | SQLite database path |
| `YARA_RULES_PATH` | `./data/yara_rules` | YARA rules directory |
| `QUARANTINE_PATH` | `./data/quarantine` | Quarantine directory |

### Directory Structure

```
backend/
├── main.py                 # FastAPI application entry
├── config.py               # Configuration settings
├── database.py             # SQLite database operations
├── scanner.py              # Core scanning logic
├── models.py               # Pydantic models
├── requirements.txt        # Dependencies
├── routes/
│   ├── scan.py             # /scan endpoints
│   ├── signatures.py       # /signatures endpoints
│   ├── quarantine.py       # /quarantine endpoints
│   └── history.py          # /history endpoints
└── data/
    ├── malguard.db         # SQLite database
    ├── yara_rules/         # YARA rule files
    └── quarantine/         # Quarantined files
```

---

## YARA Rules

Place `.yar` or `.yara` files in `data/yara_rules/`:

```yara
rule Suspicious_String {
    meta:
        description = "Detects suspicious strings"
    strings:
        $s1 = "malware" nocase
        $s2 = "payload" nocase
    condition:
        any of them
}
```

Included rules:
- `malware_rules.yar` - Common malware patterns
- EICAR test file detection

---

## Frontend Integration

### Web Frontend (React/Vite)

```typescript
// Scan files
const formData = new FormData();
formData.append('file', file);
const response = await fetch('/scan/file?scan_all=true', {
  method: 'POST',
  body: formData
});
const result = await response.json();
```

### Mobile App (React Native)

```typescript
// Upload and scan
const formData = new FormData();
formData.append('file', {
  uri: fileUri,
  type: 'application/octet-stream',
  name: fileName
});
const response = await fetch(`${API_BASE}/scan/file`, {
  method: 'POST',
  body: formData
});
```

---

## Running in Production

```bash
# Install production server
pip install gunicorn

# Run with gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

# Or use uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## API Documentation

Interactive API documentation is automatically generated:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

---

## Testing with cURL

```bash
# 1. Check health
curl http://localhost:8000/health

# 2. Seed sample signatures
curl -X POST http://localhost:8000/seed

# 3. View signatures
curl http://localhost:8000/signatures

# 4. Scan a file
curl -X POST -F "file=@eicar.com" "http://localhost:8000/scan/file?scan_all=true"

# 5. Check quarantine
curl http://localhost:8000/quarantine

# 6. View history
curl http://localhost:8000/history

# 7. Get stats
curl http://localhost:8000/stats
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "YARA not available" | `pip install yara-python` |
| Database locked | Stop other processes using the DB |
| CORS errors | Configure `allow_origins` in main.py |
| Port in use | Change port: `uvicorn main:app --port 8001` |

---

## Dependencies

```
fastapi>=0.100.0
uvicorn>=0.23.0
python-multipart>=0.0.6
aiofiles>=23.1.0
yara-python>=4.3.0
```
