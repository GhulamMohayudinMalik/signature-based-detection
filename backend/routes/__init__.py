"""
Routes Package
"""

from .signatures import router as signatures_router
from .scan import router as scan_router
from .history import router as history_router
from .quarantine import router as quarantine_router

__all__ = ["signatures_router", "scan_router", "history_router", "quarantine_router"]

