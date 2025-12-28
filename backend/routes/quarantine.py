"""
API Routes for Quarantine Management
"""

from fastapi import APIRouter, HTTPException
from pathlib import Path
from typing import Optional
import json
import shutil
from datetime import datetime

from models import MessageResponse

router = APIRouter(prefix="/quarantine", tags=["Quarantine"])


# Quarantine storage
QUARANTINE_DIR = Path(__file__).parent.parent / "data" / "quarantine"
MANIFEST_FILE = QUARANTINE_DIR / "manifest.json"


def _ensure_dir():
    """Ensure quarantine directory exists."""
    QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)


def _load_manifest() -> dict:
    """Load quarantine manifest."""
    _ensure_dir()
    if MANIFEST_FILE.exists():
        with open(MANIFEST_FILE, 'r') as f:
            return json.load(f)
    return {"files": {}, "metadata": {"created": datetime.now().isoformat()}}


def _save_manifest(manifest: dict):
    """Save quarantine manifest."""
    _ensure_dir()
    manifest["metadata"]["updated"] = datetime.now().isoformat()
    with open(MANIFEST_FILE, 'w') as f:
        json.dump(manifest, f, indent=2, default=str)


# ============== Helper function for scanner ==============
async def add_file_to_quarantine(
    file_hash: str,
    original_name: str, 
    malware_name: str,
    severity: str = "medium",
    original_path: str = None
) -> bool:
    """
    Add a detected file to quarantine.
    Called by the scanner when malware is detected.
    
    Returns True if added, False if already exists.
    """
    manifest = _load_manifest()
    
    if file_hash in manifest["files"]:
        return False  # Already in quarantine
    
    manifest["files"][file_hash] = {
        "original_name": original_name,
        "malware_name": malware_name,
        "severity": severity,
        "original_path": original_path,
        "quarantined_on": datetime.now().isoformat()
    }
    
    _save_manifest(manifest)
    return True


@router.get("")
async def list_quarantined():
    """List all quarantined files."""
    manifest = _load_manifest()
    
    files = []
    for file_hash, info in manifest["files"].items():
        files.append({
            "hash": file_hash,
            "original_name": info.get("original_name"),
            "malware_name": info.get("malware_name"),
            "severity": info.get("severity"),
            "quarantined_on": info.get("quarantined_on"),
            "original_path": info.get("original_path")
        })
    
    return {
        "total": len(files),
        "files": files
    }


@router.get("/{hash}")
async def get_quarantined(hash: str):
    """Get details of a quarantined file."""
    manifest = _load_manifest()
    
    # Try exact match first
    if hash in manifest["files"]:
        return manifest["files"][hash]
    
    # Try partial match
    matches = [h for h in manifest["files"] if h.startswith(hash)]
    if len(matches) == 1:
        return manifest["files"][matches[0]]
    elif len(matches) > 1:
        raise HTTPException(status_code=400, detail=f"Ambiguous hash: {len(matches)} matches found")
    
    raise HTTPException(status_code=404, detail="Quarantined file not found")


@router.post("", response_model=MessageResponse)
async def add_to_quarantine(
    file_hash: str,
    original_name: str,
    malware_name: str,
    severity: str = "medium",
    original_path: Optional[str] = None
):
    """Add a file to quarantine (metadata only - for tracking)."""
    manifest = _load_manifest()
    
    if file_hash in manifest["files"]:
        raise HTTPException(status_code=400, detail="File already in quarantine")
    
    manifest["files"][file_hash] = {
        "original_name": original_name,
        "malware_name": malware_name,
        "severity": severity,
        "original_path": original_path,
        "quarantined_on": datetime.now().isoformat()
    }
    
    _save_manifest(manifest)
    
    return MessageResponse(
        success=True,
        message=f"File '{original_name}' added to quarantine"
    )


@router.delete("/{hash}", response_model=MessageResponse)
async def remove_from_quarantine(hash: str):
    """Remove a file from quarantine (and delete if exists)."""
    manifest = _load_manifest()
    
    # Try exact match first
    target_hash = None
    if hash in manifest["files"]:
        target_hash = hash
    else:
        # Try partial match
        matches = [h for h in manifest["files"] if h.startswith(hash)]
        if len(matches) == 1:
            target_hash = matches[0]
        elif len(matches) > 1:
            raise HTTPException(status_code=400, detail=f"Ambiguous hash: {len(matches)} matches found")
    
    if not target_hash:
        raise HTTPException(status_code=404, detail="Quarantined file not found")
    
    # Delete quarantine file if exists
    quarantine_path = QUARANTINE_DIR / f"{target_hash[:16]}.quarantine"
    if quarantine_path.exists():
        quarantine_path.unlink()
    
    # Remove from manifest
    del manifest["files"][target_hash]
    _save_manifest(manifest)
    
    return MessageResponse(
        success=True,
        message="File removed from quarantine"
    )


@router.post("/{hash}/restore", response_model=MessageResponse)
async def restore_file(hash: str, restore_path: Optional[str] = None):
    """Restore a quarantined file (if it still exists)."""
    manifest = _load_manifest()
    
    # Try exact match first
    target_hash = None
    if hash in manifest["files"]:
        target_hash = hash
    else:
        matches = [h for h in manifest["files"] if h.startswith(hash)]
        if len(matches) == 1:
            target_hash = matches[0]
    
    if not target_hash:
        raise HTTPException(status_code=404, detail="Quarantined file not found")
    
    file_info = manifest["files"][target_hash]
    quarantine_path = QUARANTINE_DIR / f"{target_hash[:16]}.quarantine"
    
    if not quarantine_path.exists():
        # File doesn't exist physically, just remove from manifest
        del manifest["files"][target_hash]
        _save_manifest(manifest)
        return MessageResponse(
            success=True,
            message="File removed from quarantine records (file was already deleted)"
        )
    
    # Determine target path
    target = Path(restore_path) if restore_path else Path(file_info.get("original_path", "."))
    
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(quarantine_path), str(target))
        
        del manifest["files"][target_hash]
        _save_manifest(manifest)
        
        return MessageResponse(
            success=True,
            message=f"File restored to: {target}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Restore failed: {str(e)}")


@router.delete("", response_model=MessageResponse)
async def clear_quarantine():
    """Clear all quarantined files."""
    manifest = _load_manifest()
    count = len(manifest["files"])
    
    # Delete all quarantine files
    for file_hash in list(manifest["files"].keys()):
        quarantine_path = QUARANTINE_DIR / f"{file_hash[:16]}.quarantine"
        try:
            if quarantine_path.exists():
                quarantine_path.unlink()
        except Exception:
            pass
    
    # Clear manifest
    manifest["files"] = {}
    _save_manifest(manifest)
    
    return MessageResponse(
        success=True,
        message=f"Cleared {count} quarantined files"
    )


@router.get("/stats/count")
async def quarantine_count():
    """Get count of quarantined files."""
    manifest = _load_manifest()
    return {"count": len(manifest["files"])}
