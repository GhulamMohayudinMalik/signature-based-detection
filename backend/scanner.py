"""
Scanner Service
File scanning logic for the API.
"""

import hashlib
import zipfile
import io
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

from config import SUSPICIOUS_EXTENSIONS, YARA_RULES_DIR

# Optional YARA support
try:
    import yara
    YARA_AVAILABLE = True
except ImportError:
    YARA_AVAILABLE = False

# Supported archive extensions
ARCHIVE_EXTENSIONS = {'.zip'}


class ScannerService:
    """File scanning service."""
    
    def __init__(self):
        self.yara_rules = None
        if YARA_AVAILABLE:
            self._compile_yara_rules()
    
    def _compile_yara_rules(self):
        """Compile YARA rules from directory."""
        if not YARA_RULES_DIR.exists():
            return
        
        rule_files = list(YARA_RULES_DIR.glob("*.yar")) + list(YARA_RULES_DIR.glob("*.yara"))
        if not rule_files:
            return
        
        try:
            filepaths = {f"rule_{i}": str(f) for i, f in enumerate(rule_files)}
            self.yara_rules = yara.compile(filepaths=filepaths)
        except Exception as e:
            print(f"Warning: Failed to compile YARA rules: {e}")
    
    @staticmethod
    def calculate_hash(data: bytes) -> str:
        """Calculate SHA-256 hash of bytes."""
        return hashlib.sha256(data).hexdigest()
    
    @staticmethod
    def calculate_file_hash(file_path: Path) -> Optional[str]:
        """Calculate SHA-256 hash of a file."""
        try:
            hasher = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return None
    
    @staticmethod
    def is_suspicious_extension(filename: str) -> bool:
        """Check if file has suspicious extension."""
        ext = Path(filename).suffix.lower()
        return ext in SUSPICIOUS_EXTENSIONS
    
    @staticmethod
    def is_archive(filename: str) -> bool:
        """Check if file is a supported archive."""
        ext = Path(filename).suffix.lower()
        return ext in ARCHIVE_EXTENSIONS
    
    def scan_yara(self, data: bytes) -> Optional[str]:
        """Scan bytes with YARA rules."""
        if not YARA_AVAILABLE or self.yara_rules is None:
            return None
        
        try:
            matches = self.yara_rules.match(data=data)
            if matches:
                return matches[0].rule
        except Exception:
            pass
        
        return None
    
    async def extract_and_scan_archive(self, data: bytes, archive_name: str, 
                                       db, skip_non_suspicious: bool = True,
                                       max_depth: int = 3, current_depth: int = 0) -> List[Dict[str, Any]]:
        """
        Extract and scan contents of a ZIP archive.
        
        Args:
            data: Archive content as bytes
            archive_name: Name of the archive file
            db: Database instance for signature lookup
            skip_non_suspicious: Skip non-executable files
            max_depth: Maximum recursion depth for nested archives
            current_depth: Current recursion depth
        
        Returns:
            List of scan results for all files in the archive
        """
        results = []
        
        if current_depth >= max_depth:
            return results
        
        try:
            with zipfile.ZipFile(io.BytesIO(data), 'r') as zf:
                for file_info in zf.infolist():
                    # Skip directories
                    if file_info.is_dir():
                        continue
                    
                    try:
                        # Extract file content
                        file_content = zf.read(file_info.filename)
                        inner_filename = f"{archive_name}/{file_info.filename}"
                        
                        # Check if it's a nested archive
                        if self.is_archive(file_info.filename) and current_depth < max_depth - 1:
                            # Recursively scan nested archive
                            nested_results = await self.extract_and_scan_archive(
                                data=file_content,
                                archive_name=inner_filename,
                                db=db,
                                skip_non_suspicious=skip_non_suspicious,
                                max_depth=max_depth,
                                current_depth=current_depth + 1
                            )
                            results.extend(nested_results)
                        else:
                            # Scan the extracted file
                            result = await self._scan_single_file(
                                data=file_content,
                                filename=inner_filename,
                                db=db,
                                skip_non_suspicious=skip_non_suspicious
                            )
                            results.append(result)
                    except Exception as e:
                        # Log error but continue with other files
                        results.append({
                            'file_name': f"{archive_name}/{file_info.filename}",
                            'file_size': file_info.file_size,
                            'extension': Path(file_info.filename).suffix.lower(),
                            'hash': None,
                            'detected': False,
                            'malware_name': None,
                            'severity': None,
                            'reason': f'extraction_error: {str(e)}',
                            'timestamp': datetime.now()
                        })
        except zipfile.BadZipFile:
            # Not a valid ZIP file or corrupted
            pass
        except Exception as e:
            print(f"Archive scan error: {e}")
        
        return results
    
    async def _scan_single_file(self, data: bytes, filename: str,
                                db, skip_non_suspicious: bool = True) -> Dict[str, Any]:
        """
        Scan a single file's bytes (internal method).
        """
        # Import here to avoid circular imports
        from routes.quarantine import add_file_to_quarantine
        
        file_size = len(data)
        extension = Path(filename).suffix.lower()
        
        result = {
            'file_name': filename,
            'file_size': file_size,
            'extension': extension,
            'hash': None,
            'detected': False,
            'malware_name': None,
            'severity': None,
            'reason': 'clean',
            'timestamp': datetime.now()
        }
        
        # Skip non-suspicious files if requested
        if skip_non_suspicious and not self.is_suspicious_extension(filename):
            result['reason'] = 'skipped'
            await db.log_scan(result)  # Log skipped files too
            return result
        
        # Calculate hash
        file_hash = self.calculate_hash(data)
        result['hash'] = file_hash
        
        # Check signature database
        signature = await db.get_signature(file_hash)
        if signature:
            result['detected'] = True
            result['malware_name'] = signature['name']
            result['severity'] = signature.get('severity', 'medium')
            result['reason'] = 'signature_match'
            await db.log_scan(result)
            # Auto-add to quarantine
            await add_file_to_quarantine(
                file_hash=file_hash,
                original_name=filename,
                malware_name=signature['name'],
                severity=signature.get('severity', 'medium')
            )
            return result
        
        # Check YARA rules
        yara_match = self.scan_yara(data)
        if yara_match:
            result['detected'] = True
            result['malware_name'] = yara_match
            result['severity'] = 'medium'
            result['reason'] = 'yara_match'
            await db.log_scan(result)
            # Auto-add to quarantine
            await add_file_to_quarantine(
                file_hash=file_hash,
                original_name=filename,
                malware_name=yara_match,
                severity='medium'
            )
            return result
        
        # Clean file - also log to history
        result['reason'] = 'clean'
        await db.log_scan(result)  # Log clean files too
        return result
    
    async def scan_bytes(self, data: bytes, filename: str, 
                        db, skip_non_suspicious: bool = True,
                        scan_archives: bool = True) -> Dict[str, Any] | List[Dict[str, Any]]:
        """
        Scan file bytes for malware.
        
        Args:
            data: File content as bytes
            filename: Original filename
            db: Database instance for signature lookup
            skip_non_suspicious: Skip non-executable files
            scan_archives: Extract and scan archive contents
        
        Returns:
            Scan result dictionary or list of results for archives
        """
        # Check if this is an archive that should be extracted
        if scan_archives and self.is_archive(filename):
            archive_results = await self.extract_and_scan_archive(
                data=data,
                archive_name=filename,
                db=db,
                skip_non_suspicious=skip_non_suspicious
            )
            if archive_results:
                return archive_results
            # If archive was empty or couldn't be read, scan the archive file itself
        
        # Scan as regular file
        return await self._scan_single_file(
            data=data,
            filename=filename,
            db=db,
            skip_non_suspicious=skip_non_suspicious
        )
    
    async def check_hash(self, file_hash: str, db) -> Dict[str, Any]:
        """
        Check if a hash exists in the signature database.
        
        Args:
            file_hash: SHA-256 hash to check
            db: Database instance
        
        Returns:
            Result dictionary
        """
        result = {
            'hash': file_hash.lower(),
            'detected': False,
            'malware_name': None,
            'severity': None,
            'reason': 'not_found',
            'timestamp': datetime.now()
        }
        
        signature = await db.get_signature(file_hash)
        if signature:
            result['detected'] = True
            result['malware_name'] = signature['name']
            result['severity'] = signature.get('severity', 'medium')
            result['reason'] = 'signature_match'
        
        return result


# Global scanner instance
scanner_service = ScannerService()
