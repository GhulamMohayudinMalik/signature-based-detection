# MalGuard - Complete Features List

A comprehensive signature-based malware detection system with multi-platform support.

---

## 🖥️ Desktop CLI

**Technology:** Python 3.8+ | SQLite | YARA

### Core Scanning Features
| Feature | Description |
|---------|-------------|
| **Single File Scanning** | Scan individual files for malware signatures |
| **Directory Scanning** | Recursive scanning of entire directories |
| **ZIP Archive Scanning** | Extracts and scans files within ZIP archives |
| **Nested Archive Support** | Scans archives within archives (up to 3 levels deep) |
| **Executable Filtering** | Option to scan only executable file types |
| **Scan All Files Mode** | Override filtering to scan all file types |
| **Progress Indicator** | Real-time progress display during directory scans |
| **JSON Output Mode** | Machine-readable JSON output for automation |

### Detection Methods
| Feature | Description |
|---------|-------------|
| **SHA-256 Hash Matching** | Compares file hashes against signature database |
| **YARA Rules Engine** | Pattern-based detection using YARA rule files |
| **Multi-Rule Support** | Load multiple .yar/.yara rule files simultaneously |
| **Custom YARA Rules** | User-defined YARA rules in config directory |

### Signature Database
| Feature | Description |
|---------|-------------|
| **Local SQLite Storage** | Persistent signature storage in JSON format |
| **Add Signature from File** | Calculate hash and add from malware sample |
| **Add Signature Manually** | Direct hash entry with metadata |
| **Remove Signatures** | Delete individual signatures by hash |
| **List All Signatures** | Display full signature database |
| **Signature Count** | Total signatures in database |
| **Severity Levels** | Four levels: low, medium, high, critical |
| **Source Tracking** | Track where each signature came from |
| **Timestamp Tracking** | Record when signatures were added |

### Import/Export
| Feature | Description |
|---------|-------------|
| **Export to JSON** | Export entire signature database to file |
| **Import from JSON** | Bulk import signatures from JSON file |
| **Multiple Format Support** | Handles both array and object JSON formats |
| **Duplicate Detection** | Skips existing signatures during import |

### Quarantine System
| Feature | Description |
|---------|-------------|
| **Auto-Quarantine** | Automatically isolate detected malware |
| **Quarantine on Detection** | Files moved immediately upon detection |
| **Manifest Tracking** | JSON manifest with all quarantine metadata |
| **Unique File Keys** | Composite key (hash:filename) for multiple files |
| **List Quarantined Files** | View all quarantined files with details |
| **Restore by Filename** | Restore files using exact filename |
| **Restore by Hash** | Restore files using partial hash match |
| **Restore to Custom Location** | Optionally restore to different path |
| **Delete Quarantined File** | Permanently delete isolated malware |
| **Clear All Quarantine** | Bulk delete all quarantined files |
| **Original Path Preservation** | Remember original file location |
| **Quarantine Timestamp** | Track when files were quarantined |

### History & Statistics
| Feature | Description |
|---------|-------------|
| **Scan History Log** | JSONL format log of all scans |
| **Log All Results** | Records clean, skipped, and detected files |
| **Detection-Only View** | Filter to show only malware detections |
| **Statistics Dashboard** | Aggregate scanning statistics |
| **Total Scans Count** | Number of files scanned |
| **Detection Count** | Number of malware found |
| **Clean File Count** | Number of safe files |
| **Skipped File Count** | Number of filtered files |
| **Detection Rate** | Percentage of detections |

### User Interface
| Feature | Description |
|---------|-------------|
| **Colored Terminal Output** | Color-coded results (green=clean, red=detected) |
| **Severity Color Coding** | Different colors per severity level |
| **Emoji Indicators** | Visual emoji for quick status recognition |
| **Progress Percentage** | Shows scan completion percentage |
| **Detailed File Info** | Shows filename, size, hash, malware name |

### Configuration
| Feature | Description |
|---------|-------------|
| **Config Directory** | Centralized configuration folder |
| **Portable Data** | All data in user's app data folder |
| **Windows Support** | %APPDATA%\malguard\ |
| **Linux/Mac Support** | ~/.config/malguard/ |

---

## 🌐 Backend API (FastAPI)

**Technology:** Python 3.8+ | FastAPI | SQLite | YARA | Uvicorn

### API Features
| Feature | Description |
|---------|-------------|
| **RESTful API** | Standard REST endpoints |
| **OpenAPI Documentation** | Auto-generated Swagger UI at /docs |
| **ReDoc Documentation** | Alternative docs at /redoc |
| **CORS Support** | Configurable cross-origin requests |
| **Async Processing** | Non-blocking async/await operations |

### Health & Status Endpoints
| Feature | Description |
|---------|-------------|
| **Health Check** | GET /health - Server status |
| **Statistics** | GET /stats - Aggregate statistics |
| **Database Seeding** | POST /seed - Load sample signatures |

### File Scanning Endpoints
| Feature | Description |
|---------|-------------|
| **Single File Upload** | POST /scan/file - Scan one file |
| **Batch File Upload** | POST /scan/files - Scan multiple files |
| **Multipart Form Upload** | Standard file upload protocol |
| **Scan All Parameter** | Toggle executable filtering |
| **ZIP Archive Extraction** | Automatic archive content scanning |
| **Nested Archive Scanning** | Up to 3 levels of nested archives |
| **In-Memory Processing** | No temp files written to disk |
| **Batch Results** | Returns all file results in one response |

### Detection Methods
| Feature | Description |
|---------|-------------|
| **SHA-256 Signature Matching** | Hash-based malware detection |
| **YARA Pattern Matching** | Rule-based pattern detection |
| **Combined Detection** | Both methods run on each file |
| **Auto-Quarantine** | Detected files added to quarantine |
| **Detection Logging** | All detections recorded to history |

### Signature Endpoints
| Feature | Description |
|---------|-------------|
| **List Signatures** | GET /signatures - Paginated list |
| **Get Signature** | GET /signatures/{hash} - Single lookup |
| **Add Signature** | POST /signatures - Create new |
| **Delete Signature** | DELETE /signatures/{hash} - Remove |
| **Search Signatures** | GET /signatures/search?q= - Text search |
| **Filter by Severity** | GET /signatures/filter/severity/{level} |
| **Export All** | GET /signatures/export - JSON download |
| **Import JSON File** | POST /signatures/import-json - Bulk upload |
| **Bulk Add** | POST /signatures/bulk - Array of signatures |
| **Add from File** | POST /signatures/from-file - Hash a sample |

### History Endpoints
| Feature | Description |
|---------|-------------|
| **Get History** | GET /history - Scan history list |
| **Limit Parameter** | Control number of results |
| **Detected Only Filter** | Filter to malware only |
| **Clear History** | DELETE /history - Wipe logs |

### Quarantine Endpoints
| Feature | Description |
|---------|-------------|
| **List Quarantine** | GET /quarantine - All quarantined files |
| **Restore File** | POST /quarantine/{hash}/restore |
| **Delete File** | DELETE /quarantine/{hash} |
| **Clear All** | DELETE /quarantine - Remove all |

### Response Models
| Feature | Description |
|---------|-------------|
| **Typed Responses** | Pydantic model validation |
| **Error Responses** | Standardized error format |
| **Batch Responses** | Consistent multi-file format |
| **Metadata Inclusion** | Totals, counts in responses |

### Database
| Feature | Description |
|---------|-------------|
| **SQLite Backend** | Embedded database, no server needed |
| **Async Operations** | Non-blocking database access |
| **Automatic Schema** | Tables created on startup |
| **Signature Table** | Hash, name, severity, source, timestamp |
| **History Table** | Full scan results with timestamps |

### YARA Integration
| Feature | Description |
|---------|-------------|
| **YARA Rules Directory** | Load all .yar/.yara files |
| **Rule Compilation** | Compile rules on startup |
| **Pattern Matching** | Match against file content |
| **Custom Rules Support** | User-defined detection rules |

---

## 🌐 Web Frontend

**Technology:** React 18 | TypeScript | Vite | CSS3

### User Interface
| Feature | Description |
|---------|-------------|
| **Dark Theme** | Modern dark glassmorphism design |
| **Neon Accents** | Cyan/magenta neon color scheme |
| **Responsive Design** | Works on desktop, tablet, mobile |
| **Tab Navigation** | Scanner, Signatures, History, Quarantine tabs |
| **Loading States** | Spinners and progress indicators |
| **Toast Notifications** | Success/error feedback |

### Scanner Tab
| Feature | Description |
|---------|-------------|
| **Drag & Drop Upload** | Drag files onto upload zone |
| **Click to Browse** | Traditional file picker |
| **Multi-File Selection** | Upload multiple files at once |
| **File List Preview** | See selected files before scanning |
| **Remove Files** | Remove individual files from queue |
| **Scan All Toggle** | Enable/disable executable filtering |
| **Progress Bar** | Visual scan progress indicator |
| **Results Display** | Card-based results with status |
| **Malware Highlighting** | Red highlighting for detections |
| **Clean File Highlighting** | Green highlighting for safe files |
| **Severity Badges** | Color-coded severity indicators |
| **Hash Display** | Truncated SHA-256 with copy button |

### Signatures Tab
| Feature | Description |
|---------|-------------|
| **Signature Table** | Sortable list of all signatures |
| **Search Signatures** | Real-time search by name or hash |
| **Filter by Severity** | Dropdown to filter severity level |
| **Add Signature Modal** | Form to add new signatures |
| **Hash Input** | SHA-256 hash entry field |
| **Name Input** | Malware name entry field |
| **Severity Dropdown** | Select severity level |
| **Delete Signature** | Remove individual signatures |
| **Export Button** | Download signatures as JSON |
| **Import Button** | Upload JSON signature file |
| **Signature Count** | Display total signature count |
| **Pagination** | Limit display for large databases |

### History Tab
| Feature | Description |
|---------|-------------|
| **Scan History List** | All recent scan results |
| **File Name Display** | Original filename |
| **File Size Display** | Human-readable file sizes |
| **Detection Status** | Clean/Detected indicator |
| **Malware Name** | Show detected malware name |
| **Timestamp** | When scan occurred |
| **Reason Display** | signature_match, yara_match, clean |

### Quarantine Tab
| Feature | Description |
|---------|-------------|
| **Quarantine List** | All quarantined files |
| **File Details** | Name, hash, severity, date |
| **Delete Button** | Permanently delete file |
| **Clear All Button** | Delete all quarantined files |
| **Confirmation Dialogs** | Prevent accidental deletion |
| **Empty State** | Friendly message when empty |

### Dashboard Elements
| Feature | Description |
|---------|-------------|
| **Backend Status** | Online/Offline indicator |
| **Signature Count Card** | Total signatures loaded |
| **Detection Count Card** | Total malware found |
| **Scan Count Card** | Total files scanned |
| **Seed Database Button** | Quick-load sample signatures |

### Technical Features
| Feature | Description |
|---------|-------------|
| **TypeScript** | Full type safety |
| **API Error Handling** | Graceful error messages |
| **Form Validation** | Input validation before submit |
| **Debounced Search** | Efficient search queries |
| **State Management** | React hooks for state |
| **API Client** | Centralized fetch functions |

---

## 📱 Mobile App

**Technology:** React Native | Expo | TypeScript

### User Interface
| Feature | Description |
|---------|-------------|
| **Native Feel** | Platform-appropriate design |
| **Dark Theme** | Consistent with web theme |
| **Tab Navigation** | Bottom tab bar navigation |
| **Pull to Refresh** | Refresh data with pull gesture |
| **Loading Indicators** | Activity spinners |
| **Alert Dialogs** | Native confirmation dialogs |

### Scanner Screen
| Feature | Description |
|---------|-------------|
| **File Picker** | Native document picker |
| **Multi-File Selection** | Select multiple files |
| **File Preview** | Show selected file info |
| **Scan Button** | Initiate scan to backend |
| **Results Display** | Card-based results |
| **Status Indicators** | Color-coded status |
| **Severity Display** | Malware severity level |

### Signatures Screen
| Feature | Description |
|---------|-------------|
| **Signature List** | FlatList of signatures |
| **Search Bar** | Filter signatures by text |
| **Severity Filter** | Picker to filter severity |
| **Add Signature** | Modal to add new signature |
| **Delete Signature** | Swipe or button to delete |
| **Import/Export** | JSON file handling |
| **Refresh Control** | Pull to refresh list |

### History Screen
| Feature | Description |
|---------|-------------|
| **Scan History List** | Recent scan results |
| **Detection Highlighting** | Visual distinction for malware |
| **Timestamp Display** | When each scan occurred |
| **File Details** | Name, size, status |

### Quarantine Screen
| Feature | Description |
|---------|-------------|
| **Quarantine List** | All quarantined files |
| **File Details** | Name, malware type, date |
| **Delete Action** | Remove quarantined file |
| **Clear All** | Bulk delete option |

### Settings/Configuration
| Feature | Description |
|---------|-------------|
| **Backend URL Config** | Configure API server URL |
| **Connection Status** | Show backend connectivity |

### Technical Features
| Feature | Description |
|---------|-------------|
| **TypeScript** | Full type safety |
| **Expo SDK** | Managed workflow |
| **Document Picker** | expo-document-picker |
| **File System Access** | expo-file-system |
| **Async Storage** | Local data persistence |
| **API Integration** | Shared API client code |

---

## 🔄 Cross-Platform Features

### Shared Capabilities
| Feature | Desktop | Backend | Web | Mobile |
|---------|:-------:|:-------:|:---:|:------:|
| SHA-256 Scanning | ✅ | ✅ | ✅ | ✅ |
| YARA Rules | ✅ | ✅ | ❌ | ❌ |
| ZIP Archive Scanning | ✅ | ✅ | ✅ | ✅ |
| Signature Database | ✅ | ✅ | ✅ | ✅ |
| Add Signatures | ✅ | ✅ | ✅ | ✅ |
| Delete Signatures | ✅ | ✅ | ✅ | ✅ |
| Search Signatures | ❌ | ✅ | ✅ | ✅ |
| Filter by Severity | ❌ | ✅ | ✅ | ✅ |
| Import Signatures | ✅ | ✅ | ✅ | ✅ |
| Export Signatures | ✅ | ✅ | ✅ | ✅ |
| Scan History | ✅ | ✅ | ✅ | ✅ |
| Quarantine Files | ✅ | ✅ | ✅ | ✅ |
| Auto-Quarantine | ✅ | ✅ | ✅ | ✅ |
| Statistics | ✅ | ✅ | ✅ | ❌ |
| Offline Support | ✅ | ❌ | ❌ | ❌ |

### Detection Methods
| Method | Desktop | Backend | Web | Mobile |
|--------|:-------:|:-------:|:---:|:------:|
| Hash Matching | ✅ | ✅ | ✅ | ✅ |
| YARA Rules | ✅ | ✅ | ❌ | ❌ |

### Data Storage
| Storage | Desktop | Backend | Web | Mobile |
|---------|:-------:|:-------:|:---:|:------:|
| Local Files | ✅ | ✅ | ❌ | ❌ |
| SQLite | ✅ | ✅ | ❌ | ❌ |
| Backend API | ❌ | N/A | ✅ | ✅ |

---

## 📊 Statistics Summary

| Metric | Count |
|--------|-------|
| **Total Features** | 150+ |
| **Desktop Features** | 50+ |
| **Backend Features** | 45+ |
| **Web Frontend Features** | 40+ |
| **Mobile Features** | 25+ |
| **API Endpoints** | 20+ |
| **Detection Methods** | 2 (Hash + YARA) |
| **Supported Platforms** | 4 |

---

## 🧪 Testing Features

| Feature | Description |
|---------|-------------|
| **EICAR Test File** | Standard antivirus test file support |
| **Sample Signatures** | Pre-loaded test signatures via /seed |
| **Test Malware Samples** | malguard_tests/ directory |
| **JSON Test Data** | Sample import/export files |

---

*Last Updated: December 2025*
