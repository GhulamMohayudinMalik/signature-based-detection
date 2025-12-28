"""
API Routes for Scanning
"""

from fastapi import APIRouter, UploadFile, File, Form
from typing import List

from models import ScanRequest, ScanResult, ScanResponse, BatchScanResponse
from database import db
from scanner import scanner_service

router = APIRouter(prefix="/scan", tags=["Scanning"])


@router.post("/file", response_model=BatchScanResponse)
async def scan_file(
    file: UploadFile = File(...),
    scan_all: bool = Form(default=False)
):
    """
    Upload and scan a single file.
    
    - **file**: The file to scan
    - **scan_all**: If false, skip non-executable files
    
    Note: If the file is an archive (ZIP), it will be extracted and
    all contents will be scanned. The response will contain results
    for each file found inside.
    """
    content = await file.read()
    
    result = await scanner_service.scan_bytes(
        data=content,
        filename=file.filename or "unknown",
        db=db,
        skip_non_suspicious=not scan_all
    )
    
    # Handle both single result and archive results (list)
    if isinstance(result, list):
        results = [ScanResult(**r) for r in result]
    else:
        results = [ScanResult(**result)]
    
    # Calculate summary
    total = len(results)
    detected = sum(1 for r in results if r.detected)
    skipped = sum(1 for r in results if r.reason == "skipped")
    clean = total - detected - skipped
    
    return BatchScanResponse(
        success=True,
        total=total,
        clean=clean,
        detected=detected,
        skipped=skipped,
        results=results
    )


@router.post("/files", response_model=BatchScanResponse)
async def scan_files(
    files: List[UploadFile] = File(...),
    scan_all: bool = Form(default=False)
):
    """
    Upload and scan multiple files.
    
    - **files**: List of files to scan
    - **scan_all**: If false, skip non-executable files
    
    Note: Archive files (ZIP) will be extracted and their contents
    scanned individually.
    """
    results = []
    
    for file in files:
        content = await file.read()
        result = await scanner_service.scan_bytes(
            data=content,
            filename=file.filename or "unknown",
            db=db,
            skip_non_suspicious=not scan_all
        )
        
        # Handle both single result and archive results (list)
        if isinstance(result, list):
            results.extend([ScanResult(**r) for r in result])
        else:
            results.append(ScanResult(**result))
    
    # Calculate summary
    total = len(results)
    detected = sum(1 for r in results if r.detected)
    skipped = sum(1 for r in results if r.reason == "skipped")
    clean = total - detected - skipped
    
    return BatchScanResponse(
        success=True,
        total=total,
        clean=clean,
        detected=detected,
        skipped=skipped,
        results=results
    )


@router.post("/hash", response_model=ScanResponse)
async def scan_hash(request: ScanRequest):
    """
    Check if a hash exists in the malware signature database.
    
    Use this for quick lookups without uploading a file.
    """
    result = await scanner_service.check_hash(request.hash, db)
    
    # Create a minimal ScanResult
    scan_result = ScanResult(
        file_name="hash-lookup",
        file_size=0,
        extension="",
        hash=result['hash'],
        detected=result['detected'],
        malware_name=result['malware_name'],
        severity=result['severity'],
        reason=result['reason'],
        timestamp=result['timestamp']
    )
    
    return ScanResponse(
        success=True,
        result=scan_result
    )
