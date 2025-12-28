"""
MalGuard Backend API
FastAPI server for web/mobile clients.

Run with: uvicorn main:app --reload
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import CORS_ORIGINS
from database import db
from routes import signatures_router, scan_router, history_router, quarantine_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup: Connect to database
    await db.connect()
    print("✅ Database connected")
    yield
    # Shutdown: Disconnect from database
    await db.disconnect()
    print("👋 Database disconnected")


# Create FastAPI app
app = FastAPI(
    title="MalGuard API",
    description="Signature-Based Malware Detection API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(signatures_router)
app.include_router(scan_router)
app.include_router(history_router)
app.include_router(quarantine_router)


@app.get("/")
async def root():
    """API root - health check."""
    return {
        "name": "MalGuard API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    stats = await db.get_stats()
    return {
        "status": "healthy",
        "database": "connected",
        "signatures": stats['total_signatures'],
        "total_scans": stats['total_scans']
    }


@app.post("/seed")
async def seed_database():
    """Seed database with sample malware signatures."""
    import json
    from pathlib import Path
    
    # Look for sample signatures file
    sample_file = Path(__file__).parent.parent / "data" / "sample_signatures.json"
    
    if not sample_file.exists():
        return {"success": False, "message": "Sample signatures file not found"}
    
    with open(sample_file, 'r') as f:
        data = json.load(f)
    
    signatures = data.get('signatures', {})
    added = 0
    skipped = 0
    
    for hash_key, sig_data in signatures.items():
        success = await db.add_signature(
            hash=hash_key,
            name=sig_data.get('name', 'Unknown'),
            severity=sig_data.get('severity', 'medium'),
            source=sig_data.get('source', 'seed')
        )
        if success:
            added += 1
        else:
            skipped += 1
    
    return {
        "success": True,
        "message": f"Database seeded: {added} added, {skipped} skipped (already exist)"
    }


@app.get("/info")
async def info():
    """Get system information."""
    from pathlib import Path
    
    yara_dir = Path(__file__).parent.parent / "data" / "yara_rules"
    yara_rules = list(yara_dir.glob("*.yar")) if yara_dir.exists() else []
    
    stats = await db.get_stats()
    
    return {
        "name": "MalGuard Backend API",
        "version": "1.0.0",
        "features": {
            "signature_matching": True,
            "yara_rules": len(yara_rules) > 0,
            "yara_rules_count": len(yara_rules),
            "file_scanning": True,
            "hash_lookup": True,
            "bulk_import": True,
            "export": True
        },
        "database": {
            "signatures": stats['total_signatures'],
            "scans": stats['total_scans'],
            "detections": stats['total_detections']
        },
        "endpoints": {
            "scan": ["/scan/file", "/scan/files", "/scan/hash"],
            "signatures": ["/signatures", "/signatures/bulk", "/signatures/import-json", "/signatures/export"],
            "history": ["/history", "/stats"],
            "system": ["/health", "/info", "/seed"]
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

