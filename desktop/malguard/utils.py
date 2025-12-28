"""
Utility Functions
Cross-platform paths, formatting, and helper functions.
"""

import os
import sys
from pathlib import Path
from typing import Set


def get_config_dir() -> Path:
    """
    Get the configuration directory based on OS.
    
    Returns:
        Path to config directory (created if doesn't exist)
    """
    if sys.platform == "win32":
        # Windows: %APPDATA%/malguard
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData/Roaming"))
    elif sys.platform == "darwin":
        # macOS: ~/Library/Application Support/malguard
        base = Path.home() / "Library" / "Application Support"
    else:
        # Linux/Unix: ~/.config/malguard (XDG spec)
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    
    config_dir = base / "malguard"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_suspicious_extensions() -> Set[str]:
    """
    Get set of file extensions considered potentially dangerous.
    
    Returns:
        Set of lowercase extensions with leading dot
    """
    return {
        # Windows executables
        '.exe', '.dll', '.sys', '.scr', '.pif', '.com',
        # Scripts
        '.bat', '.cmd', '.ps1', '.vbs', '.vbe', '.js', '.jse', '.wsf', '.wsh',
        # Java/Python/Other
        '.jar', '.py', '.pyw', '.sh', '.bash',
        # Installers
        '.msi', '.msp', '.msu',
        # Linux/macOS
        '.elf', '.bin', '.run', '.deb', '.rpm', '.dmg', '.app', '.pkg',
        # Mobile
        '.apk', '.ipa',
        # Office macros
        '.docm', '.xlsm', '.pptm',
    }


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    return f"{size:.2f} {units[unit_index]}"


def is_suspicious_file(file_path: Path) -> bool:
    """
    Check if a file has a suspicious/executable extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if extension is in suspicious list
    """
    ext = file_path.suffix.lower()
    return ext in get_suspicious_extensions()
