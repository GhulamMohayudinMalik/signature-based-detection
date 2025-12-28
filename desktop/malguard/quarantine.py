"""
Quarantine Manager
Safely isolates detected malware files.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any

from .utils import get_config_dir


class QuarantineManager:
    """Manages quarantined files."""
    
    def __init__(self, quarantine_dir: Optional[Path] = None):
        if quarantine_dir:
            self.quarantine_dir = quarantine_dir
        else:
            self.quarantine_dir = get_config_dir() / "quarantine"
        
        self.manifest_file = self.quarantine_dir / "manifest.json"
        self._ensure_dir()
    
    def _ensure_dir(self):
        """Ensure quarantine directory exists."""
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_manifest(self) -> Dict[str, Any]:
        """Load quarantine manifest."""
        if self.manifest_file.exists():
            with open(self.manifest_file, 'r') as f:
                return json.load(f)
        return {"files": {}, "metadata": {"created": datetime.now().isoformat()}}
    
    def _save_manifest(self, manifest: Dict[str, Any]):
        """Save quarantine manifest."""
        manifest["metadata"]["updated"] = datetime.now().isoformat()
        with open(self.manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2, default=str)
    def _generate_key(self, file_hash: str, filename: str) -> str:
        """Generate a unique key for quarantine using hash and filename."""
        # Use hash:filename as composite key to allow multiple files with same hash
        safe_name = filename.replace(":", "_").replace("/", "_").replace("\\", "_")
        return f"{file_hash}:{safe_name}"
    
    def _parse_key(self, key: str) -> tuple:
        """Parse a composite key back into hash and filename."""
        if ":" in key:
            parts = key.split(":", 1)
            return parts[0], parts[1]
        return key, None
    
    def quarantine_file(self, file_path: Path, malware_name: str, 
                       file_hash: str, severity: str = "medium") -> bool:
        """
        Move a file to quarantine.
        
        Args:
            file_path: Path to the infected file
            malware_name: Name of the detected malware
            file_hash: SHA-256 hash of the file
            severity: Threat severity level
            
        Returns:
            True if successful, False otherwise
        """
        file_path = Path(file_path).resolve()
        
        if not file_path.exists():
            return False
        
        # Generate unique composite key (hash + filename)
        composite_key = self._generate_key(file_hash, file_path.name)
        
        # Generate unique quarantine filename
        import hashlib
        key_hash = hashlib.md5(composite_key.encode()).hexdigest()[:12]
        quarantine_name = f"{file_hash[:8]}_{key_hash}.quarantine"
        quarantine_path = self.quarantine_dir / quarantine_name
        
        manifest = self._load_manifest()
        
        # Check if this exact file is already quarantined
        if composite_key in manifest["files"]:
            return False  # Already quarantined
        
        try:
            # Move file to quarantine
            shutil.move(str(file_path), str(quarantine_path))
            
            # Update manifest with composite key
            manifest["files"][composite_key] = {
                "original_path": str(file_path),
                "original_name": file_path.name,
                "file_hash": file_hash,  # Store hash separately for lookup
                "quarantine_path": str(quarantine_path),
                "malware_name": malware_name,
                "severity": severity,
                "quarantined_on": datetime.now().isoformat()
            }
            self._save_manifest(manifest)
            
            return True
            
        except Exception as e:
            print(f"Error quarantining file: {e}")
            return False
    
    def restore_file(self, key_or_hash: str, restore_path: Optional[Path] = None) -> bool:
        """
        Restore a quarantined file.
        
        Args:
            key_or_hash: Composite key (hash:filename) or partial hash to match
            restore_path: Optional path to restore to (defaults to original)
            
        Returns:
            True if successful, False otherwise
        """
        manifest = self._load_manifest()
        
        target_key = None
        
        # Try exact match first
        if key_or_hash in manifest["files"]:
            target_key = key_or_hash
        else:
            # Try matching by hash prefix or exact filename
            matches = []
            for k in manifest["files"]:
                file_hash, filename = self._parse_key(k)
                # Match if: starts with input, OR filename matches exactly
                if k.startswith(key_or_hash) or (filename and filename == key_or_hash):
                    matches.append(k)
            
            if len(matches) == 1:
                target_key = matches[0]
            elif len(matches) > 1:
                print(f"⚠️  Multiple matches found. Be more specific:")
                for m in matches[:5]:
                    hash_part, name_part = self._parse_key(m)
                    print(f"   - {name_part} (hash: {hash_part[:8]}...)")
                return False
        
        if not target_key:
            return False
        
        file_info = manifest["files"][target_key]
        quarantine_path = Path(file_info["quarantine_path"])
        
        if not quarantine_path.exists():
            return False
        
        # Determine restore location
        if restore_path:
            target_path = Path(restore_path)
        else:
            target_path = Path(file_info["original_path"])
        
        try:
            # Ensure parent directory exists
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Move file back
            shutil.move(str(quarantine_path), str(target_path))
            
            # Update manifest
            del manifest["files"][target_key]
            self._save_manifest(manifest)
            
            return True
            
        except Exception as e:
            print(f"Error restoring file: {e}")
            return False
    
    def list_quarantined(self) -> List[Dict[str, Any]]:
        """List all quarantined files."""
        manifest = self._load_manifest()
        
        result = []
        for key, info in manifest["files"].items():
            # Parse hash from composite key for backwards compatibility
            file_hash = info.get("file_hash")
            if not file_hash:
                file_hash, _ = self._parse_key(key)
            
            result.append({
                "key": key,
                "hash": file_hash,
                "original_name": info.get("original_name"),
                "malware_name": info.get("malware_name"),
                "severity": info.get("severity"),
                "quarantined_on": info.get("quarantined_on"),
                "original_path": info.get("original_path")
            })
        
        return result
    
    def delete_quarantined(self, key_or_hash: str) -> bool:
        """Permanently delete a quarantined file."""
        manifest = self._load_manifest()
        
        target_key = None
        
        # Try exact match first
        if key_or_hash in manifest["files"]:
            target_key = key_or_hash
        else:
            # Try matching by hash prefix or exact filename
            matches = []
            for k in manifest["files"]:
                file_hash, filename = self._parse_key(k)
                # Match if: starts with input, OR filename matches exactly
                if k.startswith(key_or_hash) or (filename and filename == key_or_hash):
                    matches.append(k)
            
            if len(matches) == 1:
                target_key = matches[0]
            elif len(matches) > 1:
                print(f"⚠️  Multiple matches found. Be more specific:")
                for m in matches[:5]:
                    hash_part, name_part = self._parse_key(m)
                    print(f"   - {name_part} (hash: {hash_part[:8]}...)")
                return False
        
        if not target_key:
            return False
        
        file_info = manifest["files"][target_key]
        quarantine_path = Path(file_info["quarantine_path"])
        
        try:
            if quarantine_path.exists():
                quarantine_path.unlink()
            
            del manifest["files"][target_key]
            self._save_manifest(manifest)
            
            return True
            
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    def count(self) -> int:
        """Count quarantined files."""
        manifest = self._load_manifest()
        return len(manifest["files"])
    
    def clear_all(self) -> int:
        """Delete all quarantined files."""
        manifest = self._load_manifest()
        count = 0
        
        for file_hash, info in list(manifest["files"].items()):
            quarantine_path = Path(info["quarantine_path"])
            try:
                if quarantine_path.exists():
                    quarantine_path.unlink()
                del manifest["files"][file_hash]
                count += 1
            except Exception:
                pass
        
        self._save_manifest(manifest)
        return count
