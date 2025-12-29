"""
MalGuard Backend Configuration
Simple configuration without environment variables.
"""

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

# CORS - Allow all origins
CORS_ORIGINS = ["*"]

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
