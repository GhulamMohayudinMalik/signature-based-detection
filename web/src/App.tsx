import { useState, useEffect, useRef } from 'react';
import {
    healthCheck, getStats, scanFiles, getSignatures, addSignature, removeSignature,
    getHistory, getQuarantine, deleteFromQuarantine, clearQuarantine, seedDatabase,
    searchSignatures, filterSignaturesBySeverity, exportSignatures, importSignatures,
    ScanResult, Signature, StatsResponse, QuarantinedFile
} from './api';

type Tab = 'scan' | 'signatures' | 'history' | 'quarantine';

export default function App() {
    const [tab, setTab] = useState<Tab>('scan');
    const [online, setOnline] = useState(false);
    const [stats, setStats] = useState<StatsResponse | null>(null);

    useEffect(() => {
        checkBackend();
        const id = setInterval(checkBackend, 30000);
        return () => clearInterval(id);
    }, []);

    const checkBackend = async () => {
        const ok = await healthCheck();
        setOnline(ok);
        if (ok) {
            try { setStats(await getStats()); } catch { }
        }
    };

    const handleSeed = async () => {
        try {
            const result = await seedDatabase();
            alert(result.message);
            checkBackend();
        } catch {
            alert('Failed to seed database');
        }
    };

    return (
        <div className="app">
            <header className="header">
                <div className="header-inner">
                    <div className="logo">⬡ MalGuard</div>
                    <nav className="nav">
                        <button className={tab === 'scan' ? 'active' : ''} onClick={() => setTab('scan')}>
                            🔍 <span>Scanner</span>
                        </button>
                        <button className={tab === 'signatures' ? 'active' : ''} onClick={() => setTab('signatures')}>
                            🗄️ <span>Signatures</span>
                        </button>
                        <button className={tab === 'history' ? 'active' : ''} onClick={() => setTab('history')}>
                            📋 <span>History</span>
                        </button>
                        <button className={tab === 'quarantine' ? 'active' : ''} onClick={() => setTab('quarantine')}>
                            🔒 <span>Quarantine</span>
                        </button>
                    </nav>
                    <div className="status">
                        <span className={`dot ${online ? '' : 'offline'}`} />
                        {online ? 'Online' : 'Offline'}
                        {stats && <span style={{ opacity: 0.7 }}>• {stats.total_signatures} sigs</span>}
                    </div>
                </div>
            </header>

            <main className="main">
                {!online && (
                    <div className="card" style={{
                        background: 'linear-gradient(135deg, rgba(255, 51, 102, 0.1), rgba(255, 107, 107, 0.05))',
                        borderColor: 'var(--neon-red)',
                        textAlign: 'center'
                    }}>
                        <p style={{ color: 'var(--neon-red)', marginBottom: '1rem' }}>
                            ⚠️ Backend offline. Run: <code>cd backend && .\venv\Scripts\uvicorn main:app --reload</code>
                        </p>
                        <button className="btn btn-secondary btn-sm" onClick={handleSeed}>🌱 Seed Database</button>
                    </div>
                )}
                {online && stats && stats.total_signatures === 0 && (
                    <div className="card" style={{
                        background: 'linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(139, 92, 246, 0.05))',
                        borderColor: 'var(--neon-cyan)',
                        textAlign: 'center'
                    }}>
                        <p style={{ marginBottom: '1rem' }}>📭 No signatures loaded. Click to load sample signatures:</p>
                        <button className="btn btn-primary btn-sm" onClick={handleSeed}>🌱 Seed Database (25 samples)</button>
                    </div>
                )}
                {tab === 'scan' && <Scanner onDone={checkBackend} />}
                {tab === 'signatures' && <Signatures />}
                {tab === 'history' && <History />}
                {tab === 'quarantine' && <Quarantine />}
            </main>

            <footer className="footer">
                <strong>MalGuard</strong> — Next-Generation Signature-Based Malware Detection
            </footer>
        </div>
    );
}

function Scanner({ onDone }: { onDone: () => void }) {
    const [files, setFiles] = useState<File[]>([]);
    const [scanning, setScanning] = useState(false);
    const [progress, setProgress] = useState(0);
    const [results, setResults] = useState<ScanResult[]>([]);
    const [scanAll, setScanAll] = useState(true);  // Default: scan all file types
    const [dragActive, setDragActive] = useState(false);
    const inputRef = useRef<HTMLInputElement>(null);

    const handleFiles = (f: FileList | null) => {
        if (f) setFiles(prev => [...prev, ...Array.from(f)]);
    };

    const doScan = async () => {
        if (!files.length) return;
        setScanning(true);
        setProgress(0);
        const iv = setInterval(() => setProgress(p => Math.min(p + 15, 90)), 150);
        try {
            const res = await scanFiles(files, scanAll);
            setResults(res.results);
            onDone();
        } catch (e) {
            alert('Scan failed');
        }
        clearInterval(iv);
        setProgress(100);
        setScanning(false);
    };

    const formatSize = (b: number) => {
        if (!b) return '0 B';
        const i = Math.floor(Math.log(b) / Math.log(1024));
        return (b / Math.pow(1024, i)).toFixed(1) + ' ' + ['B', 'KB', 'MB', 'GB'][i];
    };

    const totals = {
        total: results.length,
        clean: results.filter(r => r.reason === 'clean').length,
        detected: results.filter(r => r.detected).length,
        skipped: results.filter(r => r.reason === 'skipped').length,
    };

    return (
        <>
            {/* Hero Section */}
            <div style={{ textAlign: 'center', marginBottom: '2.5rem', paddingTop: '1rem' }}>
                <div className="hero-icon">🛡️</div>
                <h1 className="hero-title">Malware Scanner</h1>
                <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem', maxWidth: '500px', margin: '0 auto' }}>
                    Upload files to scan for malicious signatures and threats
                </p>
            </div>

            {/* Drop Zone Card */}
            <div className="card">
                <div
                    className={`dropzone ${dragActive ? 'active' : ''}`}
                    onClick={() => inputRef.current?.click()}
                    onDragOver={e => { e.preventDefault(); setDragActive(true); }}
                    onDragLeave={() => setDragActive(false)}
                    onDrop={e => { e.preventDefault(); setDragActive(false); handleFiles(e.dataTransfer.files); }}
                >
                    <input ref={inputRef} type="file" multiple onChange={e => handleFiles(e.target.files)} />
                    <div style={{ fontSize: '3rem', marginBottom: '0.5rem' }}>
                        {dragActive ? '📥' : '📁'}
                    </div>
                    <h3>{dragActive ? 'Drop files here!' : 'Drop files here or click to browse'}</h3>
                    <p>Select any files to scan for malware signatures</p>
                </div>
                <div className="switch-row">
                    <div className={`switch ${scanAll ? 'on' : ''}`} onClick={() => setScanAll(!scanAll)} />
                    <span style={{ color: 'var(--text-secondary)' }}>Scan all file types (not just executables)</span>
                </div>
            </div>

            {/* Selected Files */}
            {files.length > 0 && (
                <div className="card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
                        <div>
                            <span className="card-title">Selected Files</span>
                            <span className="card-sub" style={{ marginLeft: '0.75rem' }}>{files.length} file(s)</span>
                        </div>
                        <button className="btn btn-secondary btn-sm" onClick={() => { setFiles([]); setResults([]); }}>
                            ✕ Clear All
                        </button>
                    </div>
                    {files.slice(0, 5).map((f, i) => (
                        <div key={i} className="item" style={{ animationDelay: `${i * 0.05}s` }}>
                            <div className="item-icon">📄</div>
                            <div className="item-info">
                                <div className="item-name">{f.name}</div>
                                <div className="item-meta">{formatSize(f.size)}</div>
                            </div>
                            <button className="btn btn-secondary btn-sm" onClick={() => setFiles(files.filter((_, j) => j !== i))}>✕</button>
                        </div>
                    ))}
                    {files.length > 5 && (
                        <p style={{ color: 'var(--text-dim)', textAlign: 'center', marginTop: '1rem' }}>
                            ...and {files.length - 5} more files
                        </p>
                    )}

                    {scanning && (
                        <div style={{ marginTop: '1.5rem' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Scanning...</span>
                                <span style={{ color: 'var(--neon-cyan)', fontSize: '0.85rem', fontWeight: 600 }}>{progress}%</span>
                            </div>
                            <div className="progress">
                                <div className="progress-bar" style={{ width: `${progress}%` }} />
                            </div>
                        </div>
                    )}

                    <button className="btn btn-primary btn-block" onClick={doScan} disabled={scanning}>
                        {scanning ? (
                            <>
                                <span className="scanning-ring" style={{ width: 20, height: 20, marginRight: 8 }}></span>
                                Scanning...
                            </>
                        ) : (
                            `🔍 Scan ${files.length} file(s)`
                        )}
                    </button>
                </div>
            )}

            {/* Results */}
            {results.length > 0 && (
                <div className="card">
                    <div className="card-title" style={{ marginBottom: '1.25rem' }}>📊 Scan Results</div>
                    <div className="stats">
                        <div className="stat">
                            <div className="stat-val">{totals.total}</div>
                            <div className="stat-label">Total Scanned</div>
                        </div>
                        <div className="stat">
                            <div className="stat-val success">{totals.clean}</div>
                            <div className="stat-label">Clean Files</div>
                        </div>
                        <div className="stat">
                            <div className="stat-val danger">{totals.detected}</div>
                            <div className="stat-label">Threats Found</div>
                        </div>
                        <div className="stat">
                            <div className="stat-val warning">{totals.skipped}</div>
                            <div className="stat-label">Skipped</div>
                        </div>
                    </div>
                    {results.map((r, i) => (
                        <div key={i} className={`item ${r.detected ? 'detected' : ''}`} style={{ animationDelay: `${i * 0.05}s` }}>
                            <div className="item-icon">{r.detected ? '🚨' : r.reason === 'skipped' ? '⏩' : '✅'}</div>
                            <div className="item-info">
                                <div className="item-name">{r.file_name}</div>
                                <div className="item-meta">{formatSize(r.file_size)} • {r.reason}</div>
                                {r.malware_name && (
                                    <div style={{ color: 'var(--neon-red)', marginTop: 4, fontWeight: 600, fontSize: '0.9rem' }}>
                                        ⚠️ {r.malware_name}
                                    </div>
                                )}
                            </div>
                            <span className={`badge ${r.detected ? 'badge-detected' : r.reason === 'skipped' ? 'badge-skipped' : 'badge-clean'}`}>
                                {r.detected ? 'Threat' : r.reason === 'skipped' ? 'Skipped' : 'Clean'}
                            </span>
                        </div>
                    ))}
                </div>
            )}
        </>
    );
}

function Signatures() {
    const [sigs, setSigs] = useState<Signature[]>([]);
    const [loading, setLoading] = useState(true);
    const [showAdd, setShowAdd] = useState(false);
    const [newSig, setNewSig] = useState({ hash: '', name: '', severity: 'medium' });
    const [search, setSearch] = useState('');
    const [filterSev, setFilterSev] = useState('');

    useEffect(() => { load(); }, []);

    const load = async () => {
        setLoading(true);
        try { setSigs((await getSignatures()).signatures); } catch { }
        setLoading(false);
    };

    const handleSearch = async () => {
        if (!search.trim()) { load(); return; }
        setLoading(true);
        try { setSigs((await searchSignatures(search)).signatures); } catch { }
        setLoading(false);
    };

    const handleFilter = async (sev: string) => {
        setFilterSev(sev);
        if (!sev) { load(); return; }
        setLoading(true);
        try { setSigs((await filterSignaturesBySeverity(sev)).signatures); } catch { }
        setLoading(false);
    };

    const handleAdd = async () => {
        if (!newSig.hash || !newSig.name) return;
        try {
            await addSignature(newSig.hash, newSig.name, newSig.severity);
            setNewSig({ hash: '', name: '', severity: 'medium' });
            setShowAdd(false);
            load();
        } catch (e: any) {
            alert(e.message || 'Failed');
        }
    };

    const handleRemove = async (hash: string) => {
        if (!confirm('Remove this signature?')) return;
        try { await removeSignature(hash); load(); } catch { alert('Failed'); }
    };

    const handleExport = async () => {
        try {
            const data = await exportSignatures();
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'signatures_export.json';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        } catch (e) {
            console.error('Export error:', e);
            alert('Export failed: ' + (e instanceof Error ? e.message : 'Unknown error'));
        }
    };

    const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;
        try {
            const result = await importSignatures(file);
            alert(result.message);
            load();
        } catch { alert('Import failed'); }
    };

    return (
        <>
            <div className="card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
                    <div>
                        <div className="card-title">🗄️ Signature Database</div>
                        <div className="card-sub">{sigs.length} malware signatures loaded</div>
                    </div>
                    <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                        <button className="btn btn-primary btn-sm" onClick={() => setShowAdd(true)}>➕ Add New</button>
                    </div>
                </div>

                {/* Search & Filter */}
                <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
                    <div style={{ flex: 1, minWidth: '200px', position: 'relative' }}>
                        <input
                            className="form-input"
                            placeholder="🔍 Search signatures..."
                            value={search}
                            onChange={e => setSearch(e.target.value)}
                            onKeyDown={e => e.key === 'Enter' && handleSearch()}
                            style={{ paddingLeft: '1rem' }}
                        />
                    </div>
                    <button className="btn btn-secondary btn-sm" onClick={handleSearch}>Search</button>
                    <select
                        className="form-input"
                        value={filterSev}
                        onChange={e => handleFilter(e.target.value)}
                        style={{ width: 'auto', minWidth: '150px' }}
                    >
                        <option value="">All Severities</option>
                        <option value="low">🟢 Low</option>
                        <option value="medium">🟡 Medium</option>
                        <option value="high">🟠 High</option>
                        <option value="critical">🔴 Critical</option>
                    </select>
                </div>

                {loading ? (
                    <div className="empty">
                        <div className="scanning-ring"></div>
                        <p>Loading signatures...</p>
                    </div>
                ) : sigs.length === 0 ? (
                    <div className="empty">
                        <div className="empty-icon">🗄️</div>
                        <p style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>No signatures found</p>
                        <p style={{ fontSize: '0.9rem' }}>Add signatures or adjust your search filters</p>
                    </div>
                ) : (
                    <div style={{ overflowX: 'auto' }}>
                        <table>
                            <thead>
                                <tr>
                                    <th>Malware Name</th>
                                    <th>Hash (SHA-256)</th>
                                    <th>Severity</th>
                                    <th>Added</th>
                                    <th></th>
                                </tr>
                            </thead>
                            <tbody>
                                {sigs.map(s => (
                                    <tr key={s.hash}>
                                        <td>
                                            <strong style={{ display: 'block', marginBottom: '0.25rem' }}>{s.name}</strong>
                                            <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>{s.source}</span>
                                        </td>
                                        <td><span className="hash">{s.hash.slice(0, 16)}...</span></td>
                                        <td><span className={`severity severity-${s.severity}`}>{s.severity}</span></td>
                                        <td style={{ color: 'var(--text-dim)', whiteSpace: 'nowrap' }}>{new Date(s.added_on).toLocaleDateString()}</td>
                                        <td><button className="btn btn-danger btn-sm" onClick={() => handleRemove(s.hash)}>🗑️</button></td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {/* Add Modal - OUTSIDE card for proper z-index */}
            {showAdd && (
                <div className="modal-bg" onClick={() => setShowAdd(false)}>
                    <div className="modal" onClick={e => e.stopPropagation()}>
                        <h2>➕ Add Signature</h2>
                        <div className="form-group">
                            <label className="form-label">SHA-256 Hash</label>
                            <input
                                className="form-input"
                                value={newSig.hash}
                                onChange={e => setNewSig({ ...newSig, hash: e.target.value })}
                                placeholder="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
                            />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Malware Name</label>
                            <input
                                className="form-input"
                                value={newSig.name}
                                onChange={e => setNewSig({ ...newSig, name: e.target.value })}
                                placeholder="Trojan.Generic.12345"
                            />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Severity Level</label>
                            <select className="form-input" value={newSig.severity} onChange={e => setNewSig({ ...newSig, severity: e.target.value })}>
                                <option value="low">🟢 Low</option>
                                <option value="medium">🟡 Medium</option>
                                <option value="high">🟠 High</option>
                                <option value="critical">🔴 Critical</option>
                            </select>
                        </div>
                        <div className="modal-btns">
                            <button className="btn btn-secondary" onClick={() => setShowAdd(false)}>Cancel</button>
                            <button className="btn btn-primary" onClick={handleAdd}>Add Signature</button>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}

function History() {
    const [entries, setEntries] = useState<ScanResult[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        (async () => {
            setLoading(true);
            try { setEntries((await getHistory()).entries); } catch { }
            setLoading(false);
        })();
    }, []);

    const formatSize = (b: number) => {
        if (!b) return '0 B';
        const i = Math.floor(Math.log(b) / Math.log(1024));
        return (b / Math.pow(1024, i)).toFixed(1) + ' ' + ['B', 'KB', 'MB', 'GB'][i];
    };

    return (
        <div className="card">
            <div style={{ marginBottom: '1.5rem' }}>
                <div className="card-title">📋 Scan History</div>
                <div className="card-sub">{entries.length} entries recorded</div>
            </div>

            {loading ? (
                <div className="empty">
                    <div className="scanning-ring"></div>
                    <p>Loading history...</p>
                </div>
            ) : entries.length === 0 ? (
                <div className="empty">
                    <div className="empty-icon">📋</div>
                    <p style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>No scan history yet</p>
                    <p style={{ fontSize: '0.9rem' }}>Scanned files will appear here</p>
                </div>
            ) : (
                <div>
                    {entries.map((e, i) => (
                        <div key={i} className={`item ${e.detected ? 'detected' : ''}`} style={{ animationDelay: `${i * 0.03}s` }}>
                            <div className="item-icon">{e.detected ? '🚨' : '✅'}</div>
                            <div className="item-info">
                                <div className="item-name">{e.file_name}</div>
                                <div className="item-meta">{formatSize(e.file_size)} • {e.reason}</div>
                                {e.malware_name && (
                                    <div style={{ color: 'var(--neon-red)', marginTop: 4, fontWeight: 600, fontSize: '0.85rem' }}>
                                        {e.malware_name}
                                    </div>
                                )}
                            </div>
                            <span style={{ color: 'var(--text-dim)', fontSize: '0.8rem', whiteSpace: 'nowrap' }}>
                                {new Date(e.timestamp).toLocaleString()}
                            </span>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

function Quarantine() {
    const [files, setFiles] = useState<QuarantinedFile[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => { load(); }, []);

    const load = async () => {
        setLoading(true);
        try { setFiles((await getQuarantine()).files); } catch { }
        setLoading(false);
    };

    const handleDelete = async (hash: string) => {
        if (!confirm('Permanently delete this quarantined file?')) return;
        try { await deleteFromQuarantine(hash); load(); } catch { alert('Failed'); }
    };

    const handleClear = async () => {
        if (!confirm('Delete ALL quarantined files? This cannot be undone.')) return;
        try { await clearQuarantine(); load(); } catch { alert('Failed'); }
    };

    return (
        <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
                <div>
                    <div className="card-title">🔒 Quarantine Zone</div>
                    <div className="card-sub">{files.length} isolated threat(s)</div>
                </div>
                {files.length > 0 && (
                    <button className="btn btn-danger btn-sm" onClick={handleClear}>🗑️ Clear All</button>
                )}
            </div>

            {loading ? (
                <div className="empty">
                    <div className="scanning-ring"></div>
                    <p>Loading quarantine...</p>
                </div>
            ) : files.length === 0 ? (
                <div className="empty">
                    <div className="empty-icon">🔒</div>
                    <p style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>Quarantine is empty</p>
                    <p style={{ fontSize: '0.9rem' }}>
                        Detected malware files will be isolated here for your safety
                    </p>
                </div>
            ) : (
                <div>
                    {files.map((f, i) => (
                        <div key={i} className="item detected" style={{ animationDelay: `${i * 0.05}s` }}>
                            <div className="item-icon">🚨</div>
                            <div className="item-info">
                                <div className="item-name">{f.original_name}</div>
                                <div style={{ color: 'var(--neon-red)', fontWeight: 600, fontSize: '0.9rem', marginTop: '0.25rem' }}>
                                    {f.malware_name}
                                </div>
                                <div className="item-meta" style={{ marginTop: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                    <span className={`severity severity-${f.severity}`}>{f.severity}</span>
                                    <span>{new Date(f.quarantined_on).toLocaleDateString()}</span>
                                </div>
                            </div>
                            <button className="btn btn-danger btn-sm" onClick={() => handleDelete(f.hash)}>🗑️</button>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
