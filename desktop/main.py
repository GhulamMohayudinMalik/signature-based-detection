#!/usr/bin/env python3
"""
MalGuard - Signature-Based Malware Detection System
Desktop CLI Entry Point

Usage:
    python main.py scan <path>              # Scan file or directory
    python main.py scan <path> --all        # Scan all files (not just executables)
    python main.py scan <path> --json       # Output results as JSON
    python main.py add <file> <name>        # Add file hash to signature database
    python main.py remove <hash>            # Remove signature from database
    python main.py list                     # List all signatures
    python main.py history                  # Show scan history
    python main.py stats                    # Show scanning statistics
    python main.py quarantine list          # List quarantined files
    python main.py quarantine restore <hash> # Restore a quarantined file
"""

import argparse
import json
import sys
from pathlib import Path

from malguard import Scanner, SignatureDatabase, ScanLogger
from malguard.hasher import FileHasher
from malguard.utils import get_config_dir, format_file_size
from malguard.colors import green, red, yellow, cyan, dim, Colors
from malguard.quarantine import QuarantineManager

# Global JSON mode flag
JSON_MODE = False

def output(data, message: str = None):
    """Output data in JSON or human-readable format."""
    if JSON_MODE:
        print(json.dumps(data, indent=2, default=str))
    elif message:
        print(message)



def cmd_scan(args, scanner: Scanner) -> int:
    """Handle scan command."""
    global JSON_MODE
    JSON_MODE = getattr(args, 'json_output', False)
    
    path = Path(args.path).resolve()
    skip_non_suspicious = not args.all_files
    
    if path.is_file():
        # Single file scan
        if not JSON_MODE:
            print(f"\n🔍 Scanning file: {cyan(path.name)}")
            print("-" * 50)
        
        result = scanner.scan_file(path, skip_non_suspicious=skip_non_suspicious)
        
        if not result:
            if JSON_MODE:
                print(json.dumps({"error": "Could not scan file"}))
            else:
                print(red("❌ Could not scan file"))
            return 1
        
        # Convert result to dict for JSON
        result_dict = {
            "file_name": result.file_name,
            "file_size": result.file_size,
            "hash": result.hash,
            "detected": result.detected,
            "malware_name": result.malware_name,
            "severity": result.severity,
            "reason": result.reason
        }
        
        if JSON_MODE:
            print(json.dumps(result_dict, indent=2))
            return 2 if result.detected else 0
        
        if result.reason == "skipped":
            print(yellow(f"⏩ Skipped (non-executable): {result.file_name}"))
            print("   Use --all to scan all file types")
            return 0
        
        if result.detected:
            print(red("🚨 MALWARE DETECTED!"))
            print(f"   File:     {result.file_name}")
            print(f"   Malware:  {red(result.malware_name)}")
            print(f"   Severity: {Colors.severity(result.severity)}{result.severity}{Colors.RESET}")
            print(f"   Reason:   {result.reason}")
            print(f"   SHA-256:  {dim(result.hash)}")
            return 2  # Special exit code for detection
        else:
            print(green(f"✅ Clean: {result.file_name}"))
            print(f"   Size:    {format_file_size(result.file_size)}")
            print(f"   SHA-256: {dim(result.hash)}")
            return 0
    
    elif path.is_dir():
        # Directory scan
        print(f"\n🔍 Scanning directory: {path}")
        if skip_non_suspicious:
            print("   (Scanning executables only. Use --all for all files)")
        print("-" * 50)
        
        def progress(current, total, file_path):
            # Simple progress indicator
            if current % 10 == 0 or current == total:
                print(f"   Progress: {current}/{total} files", end='\r')
        
        results = scanner.scan_directory(
            path, 
            skip_non_suspicious=skip_non_suspicious,
            progress_callback=progress
        )
        
        print()  # New line after progress
        
        # Summary
        summary = scanner.get_scan_summary(results)
        print("\n" + "=" * 50)
        print("📊 SCAN SUMMARY")
        print("=" * 50)
        print(f"   Total files:  {summary['total_files']}")
        print(f"   Clean:        {summary['clean']}")
        print(f"   Detected:     {summary['detected']}")
        print(f"   Skipped:      {summary['skipped']}")
        if summary.get('from_archives', 0) > 0:
            print(f"   From archives: {summary['from_archives']}")
        print(f"   Total size:   {summary['total_size']}")
        
        if summary['detected'] > 0:
            print("\n🚨 THREATS FOUND:")
            for result in results:
                if result.detected:
                    print(f"   • {result.file_name}: {result.malware_name}")
            return 2
        
        return 0
    
    else:
        print(f"❌ Path not found: {path}")
        return 1


def cmd_add(args, database: SignatureDatabase) -> int:
    """Handle add signature command."""
    file_path = Path(args.file_path).resolve()
    
    if not file_path.is_file():
        print(f"❌ File not found: {file_path}")
        return 1
    
    # Calculate hash
    file_hash = FileHasher.calculate_sha256(file_path)
    if not file_hash:
        print("❌ Could not calculate file hash")
        return 1
    
    # Add to database
    severity = args.severity if hasattr(args, 'severity') else "medium"
    
    if database.add(file_hash, args.malware_name, severity=severity, source="cli"):
        print(f"\n   File:    {file_path.name}")
        print(f"   SHA-256: {file_hash}")
        return 0
    
    return 1


def cmd_remove(args, database: SignatureDatabase) -> int:
    """Handle remove signature command."""
    if database.remove(args.hash):
        return 0
    return 1


def cmd_list(database: SignatureDatabase) -> int:
    """Handle list signatures command."""
    signatures = database.list_all()
    
    if not signatures:
        print("\n📭 No signatures in database")
        print(f"   Database path: {database.db_file}")
        return 0
    
    print(f"\n🔒 Malware Signature Database ({database.count()} signatures)")
    print(f"   Path: {database.db_file}")
    print("=" * 70)
    
    for i, (file_hash, info) in enumerate(signatures.items(), 1):
        print(f"\n{i}. {info['name']}")
        print(f"   Hash:     {file_hash}")
        print(f"   Severity: {info.get('severity', 'medium')}")
        print(f"   Added:    {info['added_on']}")
        print(f"   Source:   {info.get('source', 'unknown')}")
    
    print("\n" + "=" * 70)
    return 0


def cmd_history(logger: ScanLogger) -> int:
    """Handle history command."""
    detections = logger.get_detections_only(limit=20)
    
    if not detections:
        print("\n📭 No detections in history")
        return 0
    
    print(f"\n📋 Recent Detections (last {len(detections)})")
    print("=" * 70)
    
    for entry in detections:
        print(f"\n   🚨 {entry.get('malware_name', 'Unknown')}")
        print(f"      File:   {entry.get('file_name', 'Unknown')}")
        print(f"      Time:   {entry.get('timestamp', 'Unknown')}")
        print(f"      Reason: {entry.get('reason', 'Unknown')}")
    
    print("\n" + "=" * 70)
    return 0


def cmd_stats(logger: ScanLogger) -> int:
    """Handle stats command."""
    stats = logger.get_stats()
    
    print("\n📊 Scanning Statistics")
    print("=" * 40)
    print(f"   Total scans:     {stats['total_scans']}")
    print(f"   Detections:      {stats['detections']}")
    print(f"   Clean files:     {stats['clean']}")
    print(f"   Skipped files:   {stats['skipped']}")
    
    if stats['total_scans'] > 0:
        rate = (stats['detections'] / stats['total_scans']) * 100
        print(f"   Detection rate:  {rate:.2f}%")
    
    print("=" * 40)
    return 0


def cmd_export(args, database: SignatureDatabase) -> int:
    """Export signatures to JSON file."""
    import json
    
    output_path = Path(args.output).resolve()
    signatures = database.list_all()
    
    if not signatures:
        print("📭 No signatures to export")
        return 0
    
    export_data = {
        "signatures": signatures,
        "metadata": {
            "exported_on": str(Path(__file__).stat().st_mtime),
            "total": len(signatures),
            "source": "MalGuard Desktop CLI"
        }
    }
    
    try:
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        print(f"✅ Exported {len(signatures)} signatures to: {output_path}")
        return 0
    except Exception as e:
        print(f"❌ Export failed: {e}")
        return 1


def cmd_import(args, database: SignatureDatabase) -> int:
    """Import signatures from JSON file."""
    import json
    
    input_path = Path(args.input).resolve()
    
    if not input_path.exists():
        print(f"❌ File not found: {input_path}")
        return 1
    
    try:
        with open(input_path, 'r') as f:
            data = json.load(f)
        
        signatures = data.get('signatures', data)
        if isinstance(signatures, dict):
            # Handle both formats: {hash: {...}} or [{...}, {...}]
            items = signatures.items() if not isinstance(list(signatures.values())[0] if signatures else {}, str) else [(k, v) for k, v in signatures.items()]
        else:
            items = [(s.get('hash'), s) for s in signatures]
        
        added = 0
        skipped = 0
        
        for hash_key, sig_data in items:
            if isinstance(sig_data, dict):
                name = sig_data.get('name', 'Unknown')
                severity = sig_data.get('severity', 'medium')
                source = sig_data.get('source', 'import')
            else:
                continue
            
            if database.add(hash_key, name, severity=severity, source=source):
                added += 1
            else:
                skipped += 1
        
        print(f"✅ Import complete: {added} added, {skipped} skipped (duplicates)")
        return 0
        
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON file: {input_path}")
        return 1
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return 1


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog="malguard",
        description="MalGuard - Signature-Based Malware Detection System",
        epilog=f"Config directory: {get_config_dir()}"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan file or directory for malware')
    scan_parser.add_argument('path', help='Path to file or directory to scan')
    scan_parser.add_argument('--all', '-a', dest='all_files', action='store_true',
                            help='Scan all files (not just executables)')
    scan_parser.add_argument('--json', '-j', dest='json_output', action='store_true',
                            help='Output results as JSON')
    
    # Add signature command
    add_parser = subparsers.add_parser('add', help='Add malware signature to database')
    add_parser.add_argument('file_path', help='Path to malware sample file')
    add_parser.add_argument('malware_name', help='Malware name (e.g., "Trojan.Generic")')
    add_parser.add_argument('--severity', '-s', choices=['low', 'medium', 'high', 'critical'],
                           default='medium', help='Threat severity level')
    
    # Remove signature command
    remove_parser = subparsers.add_parser('remove', help='Remove signature from database')
    remove_parser.add_argument('hash', help='SHA-256 hash to remove')
    
    # List signatures command
    subparsers.add_parser('list', help='List all malware signatures')
    
    # History command
    subparsers.add_parser('history', help='Show recent detection history')
    
    # Stats command
    subparsers.add_parser('stats', help='Show scanning statistics')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export signatures to JSON file')
    export_parser.add_argument('output', help='Output file path (e.g., signatures.json)')
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import signatures from JSON file')
    import_parser.add_argument('input', help='Input JSON file path')
    
    # Quarantine command
    quarantine_parser = subparsers.add_parser('quarantine', help='Manage quarantined files')
    quarantine_subparsers = quarantine_parser.add_subparsers(dest='quarantine_action', help='Quarantine actions')
    
    quarantine_subparsers.add_parser('list', help='List quarantined files')
    
    qrestore_parser = quarantine_subparsers.add_parser('restore', help='Restore a quarantined file')
    qrestore_parser.add_argument('hash', help='Hash of file to restore')
    qrestore_parser.add_argument('--to', dest='restore_path', help='Optional restore path')
    
    qdelete_parser = quarantine_subparsers.add_parser('delete', help='Permanently delete a quarantined file')
    qdelete_parser.add_argument('hash', help='Hash of file to delete')
    
    quarantine_subparsers.add_parser('clear', help='Delete all quarantined files')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    # Initialize components
    database = SignatureDatabase()
    logger = ScanLogger()
    quarantine = QuarantineManager()
    scanner = Scanner(database=database, logger=logger, quarantine=quarantine, auto_quarantine=True)
    
    # Execute command
    if args.command == 'scan':
        return cmd_scan(args, scanner)
    elif args.command == 'add':
        return cmd_add(args, database)
    elif args.command == 'remove':
        return cmd_remove(args, database)
    elif args.command == 'list':
        return cmd_list(database)
    elif args.command == 'history':
        return cmd_history(logger)
    elif args.command == 'stats':
        return cmd_stats(logger)
    elif args.command == 'export':
        return cmd_export(args, database)
    elif args.command == 'import':
        return cmd_import(args, database)
    elif args.command == 'quarantine':
        return cmd_quarantine(args, quarantine)
    
    return 0


def cmd_quarantine(args, quarantine: QuarantineManager) -> int:
    """Handle quarantine commands."""
    action = getattr(args, 'quarantine_action', None)
    
    if action == 'list' or not action:
        files = quarantine.list_quarantined()
        if not files:
            print("📭 No files in quarantine")
            return 0
        
        print(f"\n🔒 Quarantined Files ({len(files)})")
        print("=" * 60)
        for f in files:
            sev_color = Colors.severity(f.get('severity', 'medium'))
            print(f"\n   {red(f['malware_name'])}")
            print(f"   Hash:     {dim(f['hash'][:32])}...")
            print(f"   Original: {f['original_name']}")
            print(f"   Severity: {sev_color}{f['severity']}{Colors.RESET}")
            print(f"   Date:     {f['quarantined_on'][:10]}")
        print()
        return 0
    
    elif action == 'restore':
        restore_path = getattr(args, 'restore_path', None)
        success = quarantine.restore_file(args.hash, restore_path)
        if success:
            print(green(f"✅ File restored successfully"))
        else:
            print(red(f"❌ Could not restore file (not found or error)"))
            return 1
        return 0
    
    elif action == 'delete':
        success = quarantine.delete_quarantined(args.hash)
        if success:
            print(green(f"✅ File permanently deleted"))
        else:
            print(red(f"❌ Could not delete file (not found)"))
            return 1
        return 0
    
    elif action == 'clear':
        count = quarantine.clear_all()
        print(green(f"✅ Cleared {count} quarantined files"))
        return 0
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

