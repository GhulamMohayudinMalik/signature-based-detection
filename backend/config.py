"""
MalGuard Backend Configuration
"""

import os
from pathlib import Path


# Base directories
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Database
DATABASE_PATH = DATA_DIR / "malguard.db"

# File uploads
UPLOAD_DIR = DATA_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100 MB

# YARA rules
YARA_RULES_DIR = DATA_DIR / "yara_rules"
YARA_RULES_DIR.mkdir(exist_ok=True)

# Security
SECRET_KEY = os.environ.get("MALGUARD_SECRET_KEY", "malguard-dev-secret-key-change-in-production")
HMAC_KEY = os.environ.get("MALGUARD_HMAC_KEY", "malguard-hmac-key-2024").encode('utf-8')

# CORS - Allow web and mobile clients
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

# Suspicious file extensions
SUSPICIOUS_EXTENSIONS = {
    '.exe', '.dll', '.sys', '.scr', '.pif', '.com',
    '.bat', '.cmd', '.ps1', '.vbs', '.vbe', '.js', '.jse', '.wsf', '.wsh',
    '.jar', '.py', '.pyw', '.sh', '.bash',
    '.msi', '.msp', '.msu',
    '.elf', '.bin', '.run', '.deb', '.rpm', '.dmg', '.app', '.pkg',
    '.apk', '.ipa',
    '.docm', '.xlsm', '.pptm',
}
