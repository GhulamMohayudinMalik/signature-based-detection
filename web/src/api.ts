// API Base URL - uses environment variable in production
const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

// ============== Types ==============

export interface ScanResult {
  file_name: string;
  file_size: number;
  extension: string;
  hash: string | null;
  detected: boolean;
  malware_name: string | null;
  severity: string | null;
  reason: string;
  timestamp: string;
}

export interface Signature {
  hash: string;
  name: string;
  severity: string;
  source: string;
  added_on: string;
}

export interface QuarantinedFile {
  hash: string;
  original_name: string;
  malware_name: string;
  severity: string;
  quarantined_on: string;
  original_path: string;
}

export interface StatsResponse {
  total_signatures: number;
  total_scans: number;
  total_detections: number;
}

export interface SystemInfo {
  name: string;
  version: string;
  features: {
    signature_matching: boolean;
    yara_rules: boolean;
    yara_rules_count: number;
    file_scanning: boolean;
    bulk_import: boolean;
    export: boolean;
  };
  database: {
    signatures: number;
    scans: number;
    detections: number;
  };
}

// ============== System ==============

export async function healthCheck(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/health`);
    return res.ok;
  } catch {
    return false;
  }
}

export async function getSystemInfo(): Promise<SystemInfo> {
  const res = await fetch(`${API_BASE}/info`);
  if (!res.ok) throw new Error('Failed to get system info');
  return res.json();
}

export async function seedDatabase(): Promise<{ success: boolean; message: string }> {
  const res = await fetch(`${API_BASE}/seed`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to seed');
  return res.json();
}

// ============== Stats ==============

export async function getStats(): Promise<StatsResponse> {
  const res = await fetch(`${API_BASE}/stats`);
  if (!res.ok) throw new Error('Failed');
  return res.json();
}

// ============== Scanning ==============

export async function scanFiles(files: File[], scanAll: boolean): Promise<{ results: ScanResult[] }> {
  const formData = new FormData();
  files.forEach(f => formData.append('files', f));
  formData.append('scan_all', String(scanAll));
  
  const res = await fetch(`${API_BASE}/scan/files`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error('Scan failed');
  return res.json();
}

export async function checkHash(hash: string): Promise<ScanResult> {
  const res = await fetch(`${API_BASE}/scan/hash`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ hash }),
  });
  if (!res.ok) throw new Error('Hash check failed');
  const data = await res.json();
  return data.result;
}

// ============== Signatures ==============

export async function getSignatures(): Promise<{ signatures: Signature[]; total: number }> {
  const res = await fetch(`${API_BASE}/signatures`);
  if (!res.ok) throw new Error('Failed');
  return res.json();
}

export async function searchSignatures(query: string): Promise<{ signatures: Signature[]; total: number }> {
  const res = await fetch(`${API_BASE}/signatures/search?q=${encodeURIComponent(query)}`);
  if (!res.ok) throw new Error('Search failed');
  return res.json();
}

export async function filterSignaturesBySeverity(severity: string): Promise<{ signatures: Signature[]; total: number }> {
  const res = await fetch(`${API_BASE}/signatures/filter/severity/${severity}`);
  if (!res.ok) throw new Error('Filter failed');
  return res.json();
}

export async function addSignature(hash: string, name: string, severity: string): Promise<void> {
  const res = await fetch(`${API_BASE}/signatures`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ hash, name, severity, source: 'web' }),
  });
  if (!res.ok) throw new Error('Failed to add');
}

export async function removeSignature(hash: string): Promise<void> {
  const res = await fetch(`${API_BASE}/signatures/${hash}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Failed to remove');
}

export async function exportSignatures(): Promise<any> {
  const res = await fetch(`${API_BASE}/signatures/export`);
  if (!res.ok) throw new Error('Export failed');
  return res.json();
}

export async function importSignatures(file: File): Promise<{ success: boolean; message: string }> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/signatures/import-json`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error('Import failed');
  return res.json();
}

export async function clearAllSignatures(): Promise<void> {
  const res = await fetch(`${API_BASE}/signatures/all`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Failed to clear');
}

// ============== History ==============

export async function getHistory(detectionsOnly: boolean = false): Promise<{ entries: ScanResult[] }> {
  const res = await fetch(`${API_BASE}/history?limit=100&detections_only=${detectionsOnly}`);
  if (!res.ok) throw new Error('Failed');
  return res.json();
}

export async function clearHistory(): Promise<void> {
  const res = await fetch(`${API_BASE}/history`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Failed to clear history');
}

// ============== Quarantine ==============

export async function getQuarantine(): Promise<{ files: QuarantinedFile[]; total: number }> {
  const res = await fetch(`${API_BASE}/quarantine`);
  if (!res.ok) throw new Error('Failed to get quarantine');
  return res.json();
}

export async function restoreFromQuarantine(hash: string): Promise<{ success: boolean; message: string }> {
  const res = await fetch(`${API_BASE}/quarantine/${hash}/restore`, { method: 'POST' });
  if (!res.ok) throw new Error('Restore failed');
  return res.json();
}

export async function deleteFromQuarantine(hash: string): Promise<void> {
  const res = await fetch(`${API_BASE}/quarantine/${hash}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Delete failed');
}

export async function clearQuarantine(): Promise<void> {
  const res = await fetch(`${API_BASE}/quarantine`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Failed to clear quarantine');
}

export async function getQuarantineCount(): Promise<number> {
  const res = await fetch(`${API_BASE}/quarantine/stats/count`);
  if (!res.ok) throw new Error('Failed');
  const data = await res.json();
  return data.count;
}
