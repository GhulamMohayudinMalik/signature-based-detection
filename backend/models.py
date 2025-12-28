"""
Pydantic Models for API Request/Response
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ============== Signature Models ==============

class SignatureBase(BaseModel):
    """Base signature model."""
    name: str = Field(..., description="Malware name (e.g., 'Trojan.GenericKD')")
    severity: str = Field(default="medium", description="Threat level: low, medium, high, critical")
    source: str = Field(default="user", description="Where this signature came from")


class SignatureCreate(SignatureBase):
    """Create signature from hash."""
    hash: str = Field(..., description="SHA-256 hash of the malware file")


class SignatureFromFile(SignatureBase):
    """Create signature by uploading a file."""
    pass  # Hash will be computed from uploaded file


class SignatureResponse(SignatureBase):
    """Signature response model."""
    hash: str
    added_on: datetime
    
    class Config:
        from_attributes = True


class SignatureListResponse(BaseModel):
    """List of signatures."""
    total: int
    signatures: List[SignatureResponse]


# ============== Scan Models ==============

class ScanRequest(BaseModel):
    """Scan request with hash only (no file upload)."""
    hash: str = Field(..., description="SHA-256 hash to check")


class ScanResult(BaseModel):
    """Single file scan result."""
    file_name: str
    file_size: int
    extension: str
    hash: Optional[str] = None
    detected: bool
    malware_name: Optional[str] = None
    severity: Optional[str] = None
    reason: str  # clean, signature_match, yara_match, skipped, error
    timestamp: datetime


class ScanResponse(BaseModel):
    """Scan response for single file."""
    success: bool
    result: ScanResult


class BatchScanResponse(BaseModel):
    """Response for multiple files."""
    success: bool
    total: int
    clean: int
    detected: int
    skipped: int
    results: List[ScanResult]


# ============== Stats Models ==============

class StatsResponse(BaseModel):
    """Dashboard statistics."""
    total_signatures: int
    total_scans: int
    total_detections: int
    recent_detections: List[ScanResult]


# ============== History Models ==============

class HistoryResponse(BaseModel):
    """Scan history response."""
    total: int
    entries: List[ScanResult]


# ============== Generic Models ==============

class MessageResponse(BaseModel):
    """Generic message response."""
    success: bool
    message: str


class ErrorResponse(BaseModel):
    """Error response."""
    success: bool = False
    error: str
    detail: Optional[str] = None
