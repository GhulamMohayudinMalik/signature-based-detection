"""
API Routes for Signatures
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List

from models import (
    SignatureCreate, SignatureResponse, SignatureListResponse,
    MessageResponse, ErrorResponse
)
from database import db
from scanner import scanner_service

router = APIRouter(prefix="/signatures", tags=["Signatures"])


@router.get("", response_model=SignatureListResponse)
async def list_signatures(limit: int = 100, offset: int = 0):
    """List all malware signatures."""
    signatures = await db.list_signatures(limit=limit, offset=offset)
    total = await db.count_signatures()
    
    return SignatureListResponse(
        total=total,
        signatures=[SignatureResponse(**sig) for sig in signatures]
    )


@router.get("/search", response_model=SignatureListResponse)
async def search_signatures(q: str):
    """Search signatures by name or hash."""
    signatures = await db.search_signatures(q)
    
    return SignatureListResponse(
        total=len(signatures),
        signatures=[SignatureResponse(**sig) for sig in signatures]
    )


@router.get("/{hash}", response_model=SignatureResponse)
async def get_signature(hash: str):
    """Get a specific signature by hash."""
    signature = await db.get_signature(hash)
    
    if not signature:
        raise HTTPException(status_code=404, detail="Signature not found")
    
    return SignatureResponse(**signature)


@router.post("", response_model=MessageResponse)
async def add_signature(signature: SignatureCreate):
    """Add a new signature from hash."""
    success = await db.add_signature(
        hash=signature.hash,
        name=signature.name,
        severity=signature.severity,
        source=signature.source
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Signature already exists")
    
    return MessageResponse(
        success=True,
        message=f"Signature '{signature.name}' added successfully"
    )


@router.post("/from-file", response_model=MessageResponse)
async def add_signature_from_file(
    file: UploadFile = File(...),
    name: str = "Unknown Malware",
    severity: str = "medium"
):
    """Add a signature by uploading a malware sample."""
    # Read file and calculate hash
    content = await file.read()
    file_hash = scanner_service.calculate_hash(content)
    
    success = await db.add_signature(
        hash=file_hash,
        name=name,
        severity=severity,
        source="upload"
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Signature already exists")
    
    return MessageResponse(
        success=True,
        message=f"Signature '{name}' added (hash: {file_hash[:16]}...)"
    )


@router.delete("/{hash}", response_model=MessageResponse)
async def remove_signature(hash: str):
    """Remove a signature from the database."""
    success = await db.remove_signature(hash)
    
    if not success:
        raise HTTPException(status_code=404, detail="Signature not found")
    
    return MessageResponse(
        success=True,
        message="Signature removed successfully"
    )


@router.get("/filter/severity/{severity}", response_model=SignatureListResponse)
async def filter_by_severity(severity: str):
    """Filter signatures by severity level."""
    if severity not in ["low", "medium", "high", "critical"]:
        raise HTTPException(status_code=400, detail="Invalid severity. Use: low, medium, high, critical")
    
    signatures = await db.filter_by_severity(severity)
    
    return SignatureListResponse(
        total=len(signatures),
        signatures=[SignatureResponse(**sig) for sig in signatures]
    )


@router.post("/bulk", response_model=MessageResponse)
async def bulk_import(signatures: List[SignatureCreate]):
    """Import multiple signatures at once."""
    added = 0
    skipped = 0
    
    for sig in signatures:
        success = await db.add_signature(
            hash=sig.hash,
            name=sig.name,
            severity=sig.severity,
            source=sig.source
        )
        if success:
            added += 1
        else:
            skipped += 1
    
    return MessageResponse(
        success=True,
        message=f"Bulk import complete: {added} added, {skipped} skipped (duplicates)"
    )


@router.post("/import-json")
async def import_from_json(file: UploadFile = File(...)):
    """Import signatures from a JSON file."""
    import json
    
    content = await file.read()
    try:
        data = json.loads(content.decode('utf-8'))
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    
    signatures = data.get('signatures', data)
    added = 0
    skipped = 0
    
    if isinstance(signatures, dict):
        # Format: {hash: {name, severity, ...}}
        for hash_key, sig_data in signatures.items():
            if isinstance(sig_data, dict):
                success = await db.add_signature(
                    hash=hash_key,
                    name=sig_data.get('name', 'Unknown'),
                    severity=sig_data.get('severity', 'medium'),
                    source=sig_data.get('source', 'import')
                )
                if success:
                    added += 1
                else:
                    skipped += 1
    else:
        # Format: [{hash, name, ...}, ...]
        for sig in signatures:
            success = await db.add_signature(
                hash=sig.get('hash'),
                name=sig.get('name', 'Unknown'),
                severity=sig.get('severity', 'medium'),
                source=sig.get('source', 'import')
            )
            if success:
                added += 1
            else:
                skipped += 1
    
    return MessageResponse(
        success=True,
        message=f"Import complete: {added} added, {skipped} skipped"
    )


@router.get("/export")
async def export_signatures():
    """Export all signatures as JSON."""
    from fastapi.responses import JSONResponse
    from datetime import datetime
    
    signatures = await db.list_signatures(limit=10000)
    
    export_data = {
        "signatures": {sig['hash']: sig for sig in signatures},
        "metadata": {
            "exported_on": datetime.now().isoformat(),
            "total": len(signatures),
            "source": "MalGuard Backend API"
        }
    }
    
    return JSONResponse(
        content=export_data,
        headers={"Content-Disposition": "attachment; filename=signatures_export.json"}
    )


@router.delete("/all", response_model=MessageResponse)
async def clear_all_signatures():
    """Remove all signatures from the database."""
    await db.clear_signatures()
    
    return MessageResponse(
        success=True,
        message="All signatures cleared"
    )

