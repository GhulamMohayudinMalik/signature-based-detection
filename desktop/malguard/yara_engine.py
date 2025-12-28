"""
YARA Engine Module
Optional YARA rule-based malware detection.
"""

from pathlib import Path
from typing import Optional, List

from .utils import get_config_dir

# YARA is optional - gracefully handle if not installed
try:
    import yara
    YARA_AVAILABLE = True
except ImportError:
    YARA_AVAILABLE = False


class YaraEngine:
    """
    YARA rule-based malware detection engine.
    
    YARA rules allow pattern-based detection beyond simple hash matching.
    """
    
    def __init__(self, rules_dir: Optional[Path] = None):
        """
        Initialize YARA engine.
        
        Args:
            rules_dir: Directory containing .yar files (default: config dir/yara_rules)
        """
        self.available = YARA_AVAILABLE
        self.rules = None
        
        if rules_dir:
            self.rules_dir = Path(rules_dir)
        else:
            self.rules_dir = get_config_dir() / "yara_rules"
        
        if self.available:
            self._compile_rules()
    
    def _compile_rules(self) -> None:
        """Compile all YARA rules from the rules directory."""
        if not self.rules_dir.exists():
            self.rules_dir.mkdir(parents=True, exist_ok=True)
            return
        
        # Find all .yar and .yara files
        rule_files = list(self.rules_dir.glob("*.yar")) + list(self.rules_dir.glob("*.yara"))
        
        if not rule_files:
            return
        
        try:
            # Compile rules from files
            filepaths = {f"rule_{i}": str(f) for i, f in enumerate(rule_files)}
            self.rules = yara.compile(filepaths=filepaths)
            print(f"✅ Compiled {len(rule_files)} YARA rule file(s)")
        except Exception as e:
            print(f"⚠️  Warning: Failed to compile YARA rules: {e}")
            self.rules = None
    
    def scan_file(self, file_path: Path) -> Optional[str]:
        """
        Scan a file with YARA rules.
        
        Args:
            file_path: Path to file to scan
            
        Returns:
            Name of matched rule, or None if no match
        """
        if not self.available or self.rules is None:
            return None
        
        try:
            matches = self.rules.match(filepath=str(file_path))
            if matches:
                # Return first matched rule name
                return matches[0].rule
        except Exception as e:
            print(f"⚠️  YARA error scanning {file_path}: {e}")
        
        return None
    
    def scan_data(self, data: bytes) -> Optional[str]:
        """
        Scan raw bytes with YARA rules.
        
        Args:
            data: Raw bytes to scan
            
        Returns:
            Name of matched rule, or None if no match
        """
        if not self.available or self.rules is None:
            return None
        
        try:
            matches = self.rules.match(data=data)
            if matches:
                return matches[0].rule
        except Exception as e:
            print(f"⚠️  YARA error scanning data: {e}")
        
        return None
    
    # Alias for consistency
    def scan_bytes(self, data: bytes) -> Optional[str]:
        """Alias for scan_data."""
        return self.scan_data(data)
    
    def reload_rules(self) -> None:
        """Reload YARA rules from disk."""
        if self.available:
            self._compile_rules()
    
    def get_rule_count(self) -> int:
        """Get number of loaded YARA rule files."""
        if not self.rules_dir.exists():
            return 0
        return len(list(self.rules_dir.glob("*.yar"))) + len(list(self.rules_dir.glob("*.yara")))
    
    def is_available(self) -> bool:
        """Check if YARA is available and rules are loaded."""
        return self.available and self.rules is not None
