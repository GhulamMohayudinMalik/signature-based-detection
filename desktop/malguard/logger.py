"""
Scan Logger Module
Logs scan results to JSONL file for audit and history.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

from .utils import get_config_dir


class ScanLogger:
    """
    Logs scan results to a JSONL (JSON Lines) file.
    Each line is a complete JSON object for easy parsing and streaming.
    """
    
    def __init__(self, log_path: Optional[Path] = None):
        """
        Initialize scan logger.
        
        Args:
            log_path: Custom path to log file (default: config dir)
        """
        if log_path:
            self.log_file = Path(log_path)
        else:
            self.log_file = get_config_dir() / "scan_history.jsonl"
        
        # Ensure parent directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log(self, result: Dict[str, Any]) -> bool:
        """
        Log a scan result.
        
        Args:
            result: Scan result dictionary
            
        Returns:
            True if logged successfully
        """
        try:
            # Add timestamp if not present
            if 'timestamp' not in result:
                result['timestamp'] = datetime.now().isoformat()
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(result, separators=(',', ':')) + '\n')
            
            return True
            
        except OSError as e:
            print(f"❌ Error writing to scan log: {e}")
            return False
    
    def get_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent scan history.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of scan results (most recent first)
        """
        if not self.log_file.exists():
            return []
        
        try:
            results = []
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            results.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
            
            # Return most recent first
            return list(reversed(results[-limit:]))
            
        except OSError as e:
            print(f"❌ Error reading scan log: {e}")
            return []
    
    def get_detections_only(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get only entries where malware was detected.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of detection results (most recent first)
        """
        history = self.get_history(limit=1000)  # Get more to filter
        detections = [r for r in history if r.get('detected', False)]
        return detections[:limit]
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get scanning statistics.
        
        Returns:
            Dictionary with total_scans, detections, clean counts
        """
        history = self.get_history(limit=10000)
        
        total = len(history)
        detections = sum(1 for r in history if r.get('detected', False))
        skipped = sum(1 for r in history if r.get('reason') == 'skipped')
        clean = total - detections - skipped
        
        return {
            'total_scans': total,
            'detections': detections,
            'clean': clean,
            'skipped': skipped
        }
    
    def clear(self) -> bool:
        """
        Clear all scan history.
        
        Returns:
            True if cleared successfully
        """
        try:
            if self.log_file.exists():
                self.log_file.unlink()
            print("✅ Scan history cleared")
            return True
        except OSError as e:
            print(f"❌ Error clearing scan log: {e}")
            return False
