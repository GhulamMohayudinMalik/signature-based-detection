"""
Scanner Module
Core file and directory scanning logic.
"""

import zipfile
import io
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable

from .hasher import FileHasher
from .database import SignatureDatabase
from .logger import ScanLogger
from .yara_engine import YaraEngine
from .utils import is_suspicious_file, format_file_size

# Supported archive extensions
ARCHIVE_EXTENSIONS = {'.zip'}


class ScanResult:
    """Represents a single file scan result."""
    
    def __init__(self, file_path: Path):
        self.file_path = str(file_path) if file_path else ""
        self.file_name = file_path.name if file_path else "unknown"
        self.file_size = file_path.stat().st_size if file_path and file_path.exists() else 0
        self.extension = file_path.suffix.lower() if file_path else ""
        self.hash: Optional[str] = None
        self.detected = False
        self.malware_name: Optional[str] = None
        self.severity: Optional[str] = None
        self.reason = "clean"
        self.timestamp = datetime.now().isoformat()
        self.from_archive: Optional[str] = None  # Archive path if extracted from ZIP
    
    @classmethod
    def from_bytes(cls, data: bytes, filename: str, archive_path: str = None) -> 'ScanResult':
        """Create ScanResult for bytes data (e.g., from archive)."""
        result = cls.__new__(cls)
        result.file_path = f"{archive_path}/{filename}" if archive_path else filename
        result.file_name = filename
        result.file_size = len(data)
        result.extension = Path(filename).suffix.lower()
        result.hash = None
        result.detected = False
        result.malware_name = None
        result.severity = None
        result.reason = "clean"
        result.timestamp = datetime.now().isoformat()
        result.from_archive = archive_path
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'file_path': self.file_path,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'extension': self.extension,
            'hash': self.hash,
            'detected': self.detected,
            'malware_name': self.malware_name,
            'severity': self.severity,
            'reason': self.reason,
            'timestamp': self.timestamp,
            'from_archive': self.from_archive
        }
    
    def __repr__(self) -> str:
        status = "🚨 DETECTED" if self.detected else "✅ Clean"
        return f"<ScanResult {self.file_name}: {status}>"


class Scanner:
    """
    Main malware scanner class.
    
    Combines hash-based signature matching, YARA rule detection,
    archive scanning, and auto-quarantine.
    """
    
    def __init__(self, 
                 database: Optional[SignatureDatabase] = None,
                 logger: Optional[ScanLogger] = None,
                 yara_engine: Optional[YaraEngine] = None,
                 quarantine=None,
                 auto_quarantine: bool = True):
        """
        Initialize scanner with optional custom components.
        
        Args:
            database: Custom signature database (default: auto-create)
            logger: Custom scan logger (default: auto-create)
            yara_engine: Custom YARA engine (default: auto-create)
            quarantine: QuarantineManager instance for auto-quarantine
            auto_quarantine: Whether to automatically quarantine detected files
        """
        self.database = database or SignatureDatabase()
        self.logger = logger or ScanLogger()
        self.yara = yara_engine or YaraEngine()
        self.hasher = FileHasher()
        self.quarantine = quarantine
        self.auto_quarantine = auto_quarantine
    
    @staticmethod
    def is_archive(filename: str) -> bool:
        """Check if file is a supported archive."""
        ext = Path(filename).suffix.lower()
        return ext in ARCHIVE_EXTENSIONS
    
    def scan_bytes(self, data: bytes, filename: str, 
                   skip_non_suspicious: bool = True,
                   archive_path: str = None) -> ScanResult:
        """
        Scan bytes data for malware.
        
        Args:
            data: File content as bytes
            filename: Original filename
            skip_non_suspicious: Skip non-executable files
            archive_path: Parent archive path if from an archive
            
        Returns:
            ScanResult object
        """
        result = ScanResult.from_bytes(data, filename, archive_path)
        
        # Skip non-suspicious files if requested
        if skip_non_suspicious and not is_suspicious_file(Path(filename)):
            result.reason = "skipped"
            self.logger.log(result.to_dict())  # Log all including skipped
            return result
        
        # Calculate hash
        file_hash = self.hasher.calculate_sha256_bytes(data)
        if not file_hash:
            result.reason = "hash_error"
            self.logger.log(result.to_dict())
            return result
        
        result.hash = file_hash
        
        # Check signature database
        signature = self.database.lookup(file_hash)
        if signature:
            result.detected = True
            result.malware_name = signature['name']
            result.severity = signature.get('severity', 'medium')
            result.reason = "signature_match"
            self.logger.log(result.to_dict())
            return result
        
        # Check YARA rules
        if self.yara.is_available():
            yara_match = self.yara.scan_bytes(data)
            if yara_match:
                result.detected = True
                result.malware_name = yara_match
                result.severity = "medium"
                result.reason = "yara_match"
                self.logger.log(result.to_dict())
                return result
        
        # File is clean
        result.reason = "clean"
        self.logger.log(result.to_dict())  # Log clean files too
        return result
    
    def scan_archive(self, archive_path: Path, 
                     skip_non_suspicious: bool = True,
                     max_depth: int = 3,
                     current_depth: int = 0) -> List[ScanResult]:
        """
        Extract and scan contents of a ZIP archive.
        
        Args:
            archive_path: Path to the archive file
            skip_non_suspicious: Skip non-executable files
            max_depth: Maximum recursion depth for nested archives
            current_depth: Current recursion depth
            
        Returns:
            List of ScanResult objects for all files in the archive
        """
        results = []
        
        if current_depth >= max_depth:
            return results
        
        try:
            with zipfile.ZipFile(archive_path, 'r') as zf:
                for file_info in zf.infolist():
                    # Skip directories
                    if file_info.is_dir():
                        continue
                    
                    try:
                        # Extract file content
                        file_content = zf.read(file_info.filename)
                        inner_filename = file_info.filename
                        archive_name = str(archive_path)
                        
                        # Check if it's a nested archive
                        if self.is_archive(inner_filename) and current_depth < max_depth - 1:
                            # Create temp file for nested archive
                            import tempfile
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tf:
                                tf.write(file_content)
                                temp_path = Path(tf.name)
                            
                            try:
                                nested_results = self.scan_archive(
                                    temp_path,
                                    skip_non_suspicious=skip_non_suspicious,
                                    max_depth=max_depth,
                                    current_depth=current_depth + 1
                                )
                                # Update archive path for nested results
                                for r in nested_results:
                                    r.from_archive = f"{archive_name}/{inner_filename}"
                                    r.file_path = f"{archive_name}/{inner_filename}/{r.file_name}"
                                results.extend(nested_results)
                            finally:
                                temp_path.unlink(missing_ok=True)
                        else:
                            # Scan the extracted file
                            result = self.scan_bytes(
                                data=file_content,
                                filename=inner_filename,
                                skip_non_suspicious=skip_non_suspicious,
                                archive_path=archive_name
                            )
                            results.append(result)
                            
                    except Exception as e:
                        # Log error but continue with other files
                        error_result = ScanResult.from_bytes(b'', file_info.filename, str(archive_path))
                        error_result.reason = f"extraction_error: {str(e)}"
                        error_result.file_size = file_info.file_size
                        self.logger.log(error_result.to_dict())
                        results.append(error_result)
                        
        except zipfile.BadZipFile:
            # Not a valid ZIP file - skip
            pass
        except Exception as e:
            print(f"⚠️  Archive scan error: {e}")
        
        return results
    
    def scan_file(self, file_path: Path, 
                  skip_non_suspicious: bool = True,
                  log_result: bool = True,
                  scan_archives: bool = True) -> Optional[ScanResult]:
        """
        Scan a single file for malware.
        
        Args:
            file_path: Path to file to scan
            skip_non_suspicious: Skip non-executable files
            log_result: Whether to log the result
            scan_archives: Extract and scan archive contents
            
        Returns:
            ScanResult object, or None if file doesn't exist
            For archives, returns the last result (or first detection)
        """
        file_path = Path(file_path).resolve()
        
        if not file_path.is_file():
            return None
        
        # Check if this is an archive
        if scan_archives and self.is_archive(str(file_path)):
            archive_results = self.scan_archive(file_path, skip_non_suspicious)
            if archive_results:
                # Return first detection, or last result if all clean
                for r in archive_results:
                    if r.detected:
                        return r
                return archive_results[-1] if archive_results else None
        
        result = ScanResult(file_path)
        
        # Skip non-suspicious files if requested
        if skip_non_suspicious and not is_suspicious_file(file_path):
            result.reason = "skipped"
            if log_result:
                self.logger.log(result.to_dict())  # Log skipped files
            return result
        
        # Calculate hash
        file_hash = self.hasher.calculate_sha256(file_path)
        if not file_hash:
            result.reason = "hash_error"
            if log_result:
                self.logger.log(result.to_dict())
            return result
        
        result.hash = file_hash
        
        # Check signature database
        signature = self.database.lookup(file_hash)
        if signature:
            result.detected = True
            result.malware_name = signature['name']
            result.severity = signature.get('severity', 'medium')
            result.reason = "signature_match"
            
            if log_result:
                self.logger.log(result.to_dict())
            
            # Auto-quarantine the file
            if self.auto_quarantine and self.quarantine:
                try:
                    self.quarantine.quarantine_file(
                        file_path, 
                        result.malware_name, 
                        file_hash, 
                        result.severity
                    )
                except Exception as e:
                    print(f"⚠️  Auto-quarantine failed: {e}")
            
            return result
        
        # Check YARA rules
        if self.yara.is_available():
            yara_match = self.yara.scan_file(file_path)
            if yara_match:
                result.detected = True
                result.malware_name = yara_match
                result.severity = "medium"
                result.reason = "yara_match"
                
                if log_result:
                    self.logger.log(result.to_dict())
                
                # Auto-quarantine the file
                if self.auto_quarantine and self.quarantine:
                    try:
                        self.quarantine.quarantine_file(
                            file_path, 
                            result.malware_name, 
                            file_hash, 
                            result.severity
                        )
                    except Exception as e:
                        print(f"⚠️  Auto-quarantine failed: {e}")
                
                return result
        
        # File is clean
        result.reason = "clean"
        if log_result:
            self.logger.log(result.to_dict())  # Log clean files too
        return result
    
    def scan_directory(self, dir_path: Path,
                       skip_non_suspicious: bool = True,
                       recursive: bool = True,
                       scan_archives: bool = True,
                       progress_callback: Optional[Callable[[int, int, Path], None]] = None
                       ) -> List[ScanResult]:
        """
        Scan all files in a directory.
        
        Args:
            dir_path: Path to directory
            skip_non_suspicious: Skip non-executable files
            recursive: Scan subdirectories
            scan_archives: Extract and scan archive contents
            progress_callback: Optional callback(current, total, file_path)
            
        Returns:
            List of ScanResult objects
        """
        dir_path = Path(dir_path).resolve()
        
        if not dir_path.is_dir():
            print(f"❌ Directory not found: {dir_path}")
            return []
        
        results: List[ScanResult] = []
        
        # Collect all files first
        if recursive:
            files = list(dir_path.rglob('*'))
        else:
            files = list(dir_path.glob('*'))
        
        files = [f for f in files if f.is_file()]
        total = len(files)
        
        for i, file_path in enumerate(files):
            try:
                if progress_callback:
                    progress_callback(i + 1, total, file_path)
                
                # Check if archive
                if scan_archives and self.is_archive(str(file_path)):
                    archive_results = self.scan_archive(file_path, skip_non_suspicious)
                    results.extend(archive_results)
                    
                    # Print detections from archives
                    for r in archive_results:
                        if r.detected:
                            print(f"🚨 DETECTED (in archive): {r.file_name} - {r.malware_name}")
                else:
                    result = self.scan_file(file_path, 
                                            skip_non_suspicious=skip_non_suspicious,
                                            log_result=True,
                                            scan_archives=False)
                    if result:
                        results.append(result)
                        
                        # Print detections immediately
                        if result.detected:
                            print(f"🚨 DETECTED: {result.file_name} - {result.malware_name}")
                        
            except PermissionError:
                print(f"⚠️  Permission denied: {file_path}")
            except Exception as e:
                print(f"⚠️  Error scanning {file_path}: {e}")
        
        return results
    
    def get_scan_summary(self, results: List[ScanResult]) -> Dict[str, Any]:
        """
        Generate summary statistics for scan results.
        
        Args:
            results: List of ScanResult objects
            
        Returns:
            Summary dictionary
        """
        total = len(results)
        detected = sum(1 for r in results if r.detected)
        skipped = sum(1 for r in results if r.reason == "skipped")
        clean = total - detected - skipped
        
        total_size = sum(r.file_size for r in results)
        from_archives = sum(1 for r in results if r.from_archive)
        
        return {
            'total_files': total,
            'detected': detected,
            'clean': clean,
            'skipped': skipped,
            'from_archives': from_archives,
            'total_size': format_file_size(total_size),
            'detection_rate': f"{(detected / max(total - skipped, 1)) * 100:.1f}%"
        }
