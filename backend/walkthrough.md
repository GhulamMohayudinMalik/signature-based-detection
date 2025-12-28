# Phase 2 Complete: Backend API

## Created Structure
```
backend/
├── main.py              # FastAPI entry point
├── config.py            # Configuration settings
├── database.py          # Async SQLite service
├── scanner.py           # File scanning service
├── models.py            # Pydantic request/response models
├── requirements.txt     # Dependencies
├── data/                # Created at runtime
│   ├── malguard.db     # SQLite database
│   └── yara_rules/     # YARA rule files
└── routes/
    ├── __init__.py
    ├── signatures.py    # /signatures endpoints
    ├── scan.py          # /scan endpoints
    └── history.py       # /history, /stats endpoints
```

## API Endpoints

### Scanning
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/scan/file` | Upload and scan a file |
| POST | `/scan/files` | Upload and scan multiple files |
| POST | `/scan/hash` | Check hash against database |

### Signatures
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/signatures` | List all signatures |
| GET | `/signatures/search?q=` | Search signatures |
| GET | `/signatures/{hash}` | Get specific signature |
| POST | `/signatures` | Add signature from hash |
| POST | `/signatures/from-file` | Add signature by upload |
| DELETE | `/signatures/{hash}` | Remove signature |

### History & Stats
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/history` | Get scan history |
| DELETE | `/history` | Clear history |
| GET | `/stats` | Dashboard statistics |
| GET | `/health` | Health check |

## Run the Server
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Then visit: http://localhost:8000/docs for Swagger UI
