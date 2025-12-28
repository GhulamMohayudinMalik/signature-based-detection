"""
Signature Database Module
Stores and manages malware hash signatures with HMAC integrity verification.
"""

import os
import json
import hmac
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Any

from .utils import get_config_dir


class SignatureDatabase:
    """
    Manages malware signature database with tamper protection.
    
    Signatures are stored as: {hash: {name, severity, added_on, source}}
    Database file is HMAC-signed to detect tampering.
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize signature database.
        
        Args:
            db_path: Custom path to database file (default: config dir)
        """
        if db_path:
            self.db_file = Path(db_path)
        else:
            self.db_file = get_config_dir() / "signatures.json"
        
        # Secret key for HMAC signing (in production, use env var or secure storage)
        self._secret_key = os.environ.get(
            "MALGUARD_DB_KEY", 
            "malguard_signature_db_secret_key_2024"
        ).encode('utf-8')
        
        self.signatures: Dict[str, Dict[str, Any]] = {}
        self._load()
    
    def _compute_signature(self, data: str) -> str:
        """Compute HMAC-SHA256 signature of data."""
        return hmac.new(self._secret_key, data.encode('utf-8'), hashlib.sha256).hexdigest()
    
    def _load(self) -> None:
        """Load signatures from file with integrity check."""
        if not self.db_file.exists():
            self.signatures = {}
            return
        
        try:
            with open(self.db_file, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            # Verify structure
            if 'signature' not in raw_data or 'data' not in raw_data:
                print("❌ Invalid signature database format")
                self.signatures = {}
                return
            
            # Verify HMAC
            stored_sig = raw_data['signature']
            data_str = json.dumps(raw_data['data'], sort_keys=True, separators=(',', ':'))
            computed_sig = self._compute_signature(data_str)
            
            if not hmac.compare_digest(stored_sig, computed_sig):
                print("⚠️  WARNING: Signature database has been tampered with!")
                self.signatures = {}
                return
            
            self.signatures = raw_data['data']
            
        except (json.JSONDecodeError, OSError) as e:
            print(f"❌ Error loading signature database: {e}")
            self.signatures = {}
    
    def _save(self) -> bool:
        """Save signatures to file with HMAC signature."""
        try:
            # Create parent directory if needed
            self.db_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Compute signature
            data_str = json.dumps(self.signatures, sort_keys=True, separators=(',', ':'))
            signature = self._compute_signature(data_str)
            
            # Save signed database
            signed_db = {
                'signature': signature,
                'data': self.signatures
            }
            
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(signed_db, f, indent=2)
            
            return True
            
        except OSError as e:
            print(f"❌ Error saving signature database: {e}")
            return False
    
    def add(self, file_hash: str, name: str, severity: str = "medium", 
            source: str = "user") -> bool:
        """
        Add a new signature to the database.
        
        Args:
            file_hash: SHA-256 hash of the malware file
            name: Malware name/identifier (e.g., "Trojan.GenericKD")
            severity: Threat level (low, medium, high, critical)
            source: Where this signature came from
            
        Returns:
            True if added successfully, False if already exists or error
        """
        file_hash = file_hash.lower()
        
        if file_hash in self.signatures:
            print(f"ℹ️  Signature already exists: {name}")
            return False
        
        self.signatures[file_hash] = {
            'name': name,
            'severity': severity,
            'added_on': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'source': source
        }
        
        if self._save():
            print(f"✅ Added signature: {name} ({file_hash[:16]}...)")
            return True
        return False
    
    def remove(self, file_hash: str) -> bool:
        """
        Remove a signature from the database.
        
        Args:
            file_hash: SHA-256 hash to remove
            
        Returns:
            True if removed, False if not found
        """
        file_hash = file_hash.lower()
        
        if file_hash not in self.signatures:
            print(f"❌ Signature not found: {file_hash[:16]}...")
            return False
        
        name = self.signatures[file_hash]['name']
        del self.signatures[file_hash]
        
        if self._save():
            print(f"✅ Removed signature: {name}")
            return True
        return False
    
    def lookup(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """
        Look up a hash in the database.
        
        Args:
            file_hash: SHA-256 hash to look up
            
        Returns:
            Signature info dict if found, None otherwise
        """
        return self.signatures.get(file_hash.lower())
    
    def list_all(self) -> Dict[str, Dict[str, Any]]:
        """Get all signatures."""
        return self.signatures.copy()
    
    def count(self) -> int:
        """Get number of signatures in database."""
        return len(self.signatures)
    
    def import_signatures(self, file_path: Path) -> int:
        """
        Import signatures from a JSON file.
        
        Expected format: {"hash": {"name": "...", "severity": "..."}, ...}
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Number of signatures imported
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            count = 0
            for file_hash, info in data.items():
                if file_hash.lower() not in self.signatures:
                    self.signatures[file_hash.lower()] = {
                        'name': info.get('name', 'Unknown'),
                        'severity': info.get('severity', 'medium'),
                        'added_on': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'source': info.get('source', 'import')
                    }
                    count += 1
            
            if count > 0:
                self._save()
            
            print(f"✅ Imported {count} signatures")
            return count
            
        except (json.JSONDecodeError, OSError) as e:
            print(f"❌ Error importing signatures: {e}")
            return 0
    
    def export_signatures(self, file_path: Path) -> bool:
        """
        Export signatures to a JSON file.
        
        Args:
            file_path: Path to output file
            
        Returns:
            True if exported successfully
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.signatures, f, indent=2)
            print(f"✅ Exported {len(self.signatures)} signatures to {file_path}")
            return True
        except OSError as e:
            print(f"❌ Error exporting signatures: {e}")
            return False
