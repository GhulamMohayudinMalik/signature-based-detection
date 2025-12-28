"""
API Routes for History and Statistics
"""

from fastapi import APIRouter

from models import HistoryResponse, StatsResponse, ScanResult, MessageResponse
from database import db

router = APIRouter(tags=["History & Stats"])


@router.get("/history", response_model=HistoryResponse)
async def get_history(limit: int = 100, detections_only: bool = False):
    """
    Get scan history.
    
    - **limit**: Maximum entries to return
    - **detections_only**: Only show entries where malware was detected
    """
    entries = await db.get_history(limit=limit, detections_only=detections_only)
    
    # Convert to ScanResult objects
    results = []
    for entry in entries:
        results.append(ScanResult(
            file_name=entry['file_name'],
            file_size=entry['file_size'] or 0,
            extension=entry['extension'] or '',
            hash=entry['hash'],
            detected=bool(entry['detected']),
            malware_name=entry['malware_name'],
            severity=entry['severity'],
            reason=entry['reason'] or 'unknown',
            timestamp=entry['timestamp']
        ))
    
    return HistoryResponse(
        total=len(results),
        entries=results
    )


@router.delete("/history", response_model=MessageResponse)
async def clear_history():
    """Clear all scan history."""
    count = await db.clear_history()
    
    return MessageResponse(
        success=True,
        message=f"Cleared {count} history entries"
    )


@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get dashboard statistics."""
    stats = await db.get_stats()
    
    # Get recent detections
    recent = await db.get_history(limit=5, detections_only=True)
    recent_results = []
    for entry in recent:
        recent_results.append(ScanResult(
            file_name=entry['file_name'],
            file_size=entry['file_size'] or 0,
            extension=entry['extension'] or '',
            hash=entry['hash'],
            detected=bool(entry['detected']),
            malware_name=entry['malware_name'],
            severity=entry['severity'],
            reason=entry['reason'] or 'unknown',
            timestamp=entry['timestamp']
        ))
    
    return StatsResponse(
        total_signatures=stats['total_signatures'],
        total_scans=stats['total_scans'],
        total_detections=stats['total_detections'],
        recent_detections=recent_results
    )
