"""
File Hashing Module
Computes cryptographic hashes (SHA-256) for files.
"""

import hashlib
from pathlib import Path
from typing import Optional


class FileHasher:
    """Handles file hash computation."""
    
    CHUNK_SIZE = 4096  # Read files in 4KB chunks for memory efficiency
    
    @staticmethod
    def calculate_sha256(file_path: Path) -> Optional[str]:
        """
        Calculate SHA-256 hash of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Hex string of SHA-256 hash, or None if error
        """
        try:
            hasher = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(FileHasher.CHUNK_SIZE), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except (OSError, IOError, PermissionError) as e:
            print(f"❌ Hash error for {file_path}: {e}")
            return None
    
    @staticmethod
    def calculate_sha256_bytes(data: bytes) -> Optional[str]:
        """
        Calculate SHA-256 hash of bytes data.
        
        Args:
            data: Bytes to hash
            
        Returns:
            Hex string of SHA-256 hash, or None if error
        """
        try:
            return hashlib.sha256(data).hexdigest()
        except Exception as e:
            print(f"❌ Hash error: {e}")
            return None
    
    @staticmethod
    def calculate_hash(file_path: Path, algorithm: str = 'sha256') -> Optional[str]:
        """
        Calculate hash using specified algorithm.
        
        Args:
            file_path: Path to the file
            algorithm: Hash algorithm (sha256, md5, sha1)
            
        Returns:
            Hex string of hash, or None if error
        """
        try:
            hasher = hashlib.new(algorithm)
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(FileHasher.CHUNK_SIZE), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except (OSError, IOError, PermissionError) as e:
            print(f"❌ Hash error for {file_path}: {e}")
            return None
        except ValueError as e:
            print(f"❌ Invalid hash algorithm '{algorithm}': {e}")
            return None
