/**
 * API Client for MalGuard Mobile
 * 
 * PRODUCTION: Update API_BASE to your deployed backend URL before building
 */

// ========== API CONFIGURATION ==========
// For production: Replace with your AWS backend URL (e.g., https://api.malguard.com)
// For development: Use your local IP address
const API_BASE = 'http://192.168.100.113:8000'; // UPDATE BEFORE PRODUCTION BUILD

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
  recent_detections: ScanResult[];
}

export interface SystemInfo {
  name: string;
  version: string;
  features: {
    signature_matching: boolean;
    yara_rules: boolean;
    yara_rules_count: number;
  };
  database: {
    signatures: number;
    scans: number;
    detections: number;
  };
}

// ============== API Methods ==============

export const api = {
  // System
  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE}/health`);
      return response.ok;
    } catch {
      return false;
    }
  },

  async getSystemInfo(): Promise<SystemInfo> {
    const response = await fetch(`${API_BASE}/info`);
    if (!response.ok) throw new Error('Failed to get system info');
    return response.json();
  },

  async seedDatabase(): Promise<{ success: boolean; message: string }> {
    const response = await fetch(`${API_BASE}/seed`, { method: 'POST' });
    if (!response.ok) throw new Error('Failed to seed');
    return response.json();
  },

  // Stats
  async getStats(): Promise<StatsResponse> {
    const response = await fetch(`${API_BASE}/stats`);
    if (!response.ok) throw new Error('Failed to fetch stats');
    return response.json();
  },

  // Scanning
  async scanFile(uri: string, name: string, type: string): Promise<ScanResult> {
    const formData = new FormData();
    formData.append('file', {
      uri,
      name,
      type,
    } as any);
    formData.append('scan_all', 'true');

    const response = await fetch(`${API_BASE}/scan/file`, {
      method: 'POST',
      body: formData,
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    if (!response.ok) throw new Error('Scan failed');
    const data = await response.json();
    return data.result;
  },

  async checkHash(hash: string): Promise<ScanResult> {
    const response = await fetch(`${API_BASE}/scan/hash`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ hash }),
    });

    if (!response.ok) throw new Error('Hash check failed');
    const data = await response.json();
    return data.result;
  },

  // Signatures
  async getSignatures(): Promise<Signature[]> {
    const response = await fetch(`${API_BASE}/signatures`);
    if (!response.ok) throw new Error('Failed to fetch signatures');
    const data = await response.json();
    return data.signatures;
  },

  async searchSignatures(query: string): Promise<Signature[]> {
    const response = await fetch(`${API_BASE}/signatures/search?q=${encodeURIComponent(query)}`);
    if (!response.ok) throw new Error('Search failed');
    const data = await response.json();
    return data.signatures;
  },

  async filterSignaturesBySeverity(severity: string): Promise<Signature[]> {
    const response = await fetch(`${API_BASE}/signatures/filter/severity/${severity}`);
    if (!response.ok) throw new Error('Filter failed');
    const data = await response.json();
    return data.signatures;
  },

  // History
  async getHistory(limit: number = 50): Promise<ScanResult[]> {
    const response = await fetch(`${API_BASE}/history?limit=${limit}`);
    if (!response.ok) throw new Error('Failed to fetch history');
    const data = await response.json();
    return data.entries;
  },

  // Quarantine
  async getQuarantine(): Promise<QuarantinedFile[]> {
    const response = await fetch(`${API_BASE}/quarantine`);
    if (!response.ok) throw new Error('Failed to get quarantine');
    const data = await response.json();
    return data.files;
  },

  async deleteFromQuarantine(hash: string): Promise<void> {
    const response = await fetch(`${API_BASE}/quarantine/${hash}`, { method: 'DELETE' });
    if (!response.ok) throw new Error('Delete failed');
  },

  async clearQuarantine(): Promise<void> {
    const response = await fetch(`${API_BASE}/quarantine`, { method: 'DELETE' });
    if (!response.ok) throw new Error('Failed to clear quarantine');
  },

  async getQuarantineCount(): Promise<number> {
    const response = await fetch(`${API_BASE}/quarantine/stats/count`);
    if (!response.ok) throw new Error('Failed');
    const data = await response.json();
    return data.count;
  },
};
