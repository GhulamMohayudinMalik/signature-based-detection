"""
MalGuard - Signature-Based Malware Detection System
Desktop CLI Package
"""

from .scanner import Scanner
from .database import SignatureDatabase
from .hasher import FileHasher
from .logger import ScanLogger

__version__ = "1.0.0"
__all__ = ["Scanner", "SignatureDatabase", "FileHasher", "ScanLogger"]
