"""
Database Service
SQLite-based signature storage and scan history.
"""

import aiosqlite
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from config import DATABASE_PATH


class Database:
    """Async SQLite database service."""
    
    def __init__(self, db_path: Path = DATABASE_PATH):
        self.db_path = db_path
        self._connection: Optional[aiosqlite.Connection] = None
    
    async def connect(self):
        """Connect to database and create tables."""
        self._connection = await aiosqlite.connect(self.db_path)
        self._connection.row_factory = aiosqlite.Row
        await self._create_tables()
    
    async def disconnect(self):
        """Close database connection."""
        if self._connection:
            await self._connection.close()
    
    async def _create_tables(self):
        """Create database tables if they don't exist."""
        await self._connection.executescript("""
            CREATE TABLE IF NOT EXISTS signatures (
                hash TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                severity TEXT DEFAULT 'medium',
                source TEXT DEFAULT 'user',
                added_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS scan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                file_size INTEGER,
                extension TEXT,
                hash TEXT,
                detected INTEGER DEFAULT 0,
                malware_name TEXT,
                severity TEXT,
                reason TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_scan_detected ON scan_history(detected);
            CREATE INDEX IF NOT EXISTS idx_scan_timestamp ON scan_history(timestamp);
        """)
        await self._connection.commit()
    
    # ============== Signature Methods ==============
    
    async def add_signature(self, hash: str, name: str, 
                           severity: str = "medium", 
                           source: str = "user") -> bool:
        """Add a new signature to the database."""
        try:
            await self._connection.execute(
                "INSERT INTO signatures (hash, name, severity, source) VALUES (?, ?, ?, ?)",
                (hash.lower(), name, severity, source)
            )
            await self._connection.commit()
            return True
        except aiosqlite.IntegrityError:
            return False  # Already exists
    
    async def remove_signature(self, hash: str) -> bool:
        """Remove a signature from the database."""
        cursor = await self._connection.execute(
            "DELETE FROM signatures WHERE hash = ?",
            (hash.lower(),)
        )
        await self._connection.commit()
        return cursor.rowcount > 0
    
    async def get_signature(self, hash: str) -> Optional[Dict[str, Any]]:
        """Look up a signature by hash."""
        cursor = await self._connection.execute(
            "SELECT * FROM signatures WHERE hash = ?",
            (hash.lower(),)
        )
        row = await cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    async def list_signatures(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List all signatures."""
        cursor = await self._connection.execute(
            "SELECT * FROM signatures ORDER BY added_on DESC LIMIT ? OFFSET ?",
            (limit, offset)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    
    async def count_signatures(self) -> int:
        """Count total signatures."""
        cursor = await self._connection.execute("SELECT COUNT(*) FROM signatures")
        row = await cursor.fetchone()
        return row[0]
    
    async def search_signatures(self, query: str) -> List[Dict[str, Any]]:
        """Search signatures by name or hash."""
        cursor = await self._connection.execute(
            "SELECT * FROM signatures WHERE name LIKE ? OR hash LIKE ? LIMIT 50",
            (f"%{query}%", f"%{query}%")
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    
    async def filter_by_severity(self, severity: str) -> List[Dict[str, Any]]:
        """Filter signatures by severity level."""
        cursor = await self._connection.execute(
            "SELECT * FROM signatures WHERE severity = ? ORDER BY added_on DESC",
            (severity,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    
    async def clear_signatures(self) -> int:
        """Remove all signatures from the database."""
        cursor = await self._connection.execute("DELETE FROM signatures")
        await self._connection.commit()
        return cursor.rowcount
    
    # ============== Scan History Methods ==============
    
    async def log_scan(self, result: Dict[str, Any]) -> int:
        """Log a scan result."""
        cursor = await self._connection.execute(
            """INSERT INTO scan_history 
               (file_name, file_size, extension, hash, detected, malware_name, severity, reason)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                result.get('file_name'),
                result.get('file_size', 0),
                result.get('extension'),
                result.get('hash'),
                1 if result.get('detected') else 0,
                result.get('malware_name'),
                result.get('severity'),
                result.get('reason')
            )
        )
        await self._connection.commit()
        return cursor.lastrowid
    
    async def get_history(self, limit: int = 100, 
                         detections_only: bool = False) -> List[Dict[str, Any]]:
        """Get scan history."""
        if detections_only:
            query = "SELECT * FROM scan_history WHERE detected = 1 ORDER BY timestamp DESC LIMIT ?"
        else:
            query = "SELECT * FROM scan_history ORDER BY timestamp DESC LIMIT ?"
        
        cursor = await self._connection.execute(query, (limit,))
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    
    async def get_stats(self) -> Dict[str, int]:
        """Get scanning statistics."""
        cursor = await self._connection.execute("""
            SELECT 
                COUNT(*) as total_scans,
                SUM(CASE WHEN detected = 1 THEN 1 ELSE 0 END) as total_detections
            FROM scan_history
        """)
        row = await cursor.fetchone()
        
        sig_cursor = await self._connection.execute("SELECT COUNT(*) FROM signatures")
        sig_row = await sig_cursor.fetchone()
        
        return {
            'total_scans': row['total_scans'] or 0,
            'total_detections': row['total_detections'] or 0,
            'total_signatures': sig_row[0] or 0
        }
    
    async def clear_history(self) -> int:
        """Clear all scan history."""
        cursor = await self._connection.execute("DELETE FROM scan_history")
        await self._connection.commit()
        return cursor.rowcount


# Global database instance
db = Database()
