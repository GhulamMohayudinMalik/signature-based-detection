import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    ScrollView,
    TouchableOpacity,
    Alert,
    ActivityIndicator,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import * as DocumentPicker from 'expo-document-picker';
import { styles, colors } from './src/styles';
import { api, ScanResult, StatsResponse, QuarantinedFile } from './src/api';

type Tab = 'scan' | 'history' | 'quarantine' | 'stats';

export default function App() {
    const [activeTab, setActiveTab] = useState<Tab>('scan');
    const [online, setOnline] = useState(false);
    const [loading, setLoading] = useState(false);
    const [scanning, setScanning] = useState(false);
    const [stats, setStats] = useState<StatsResponse | null>(null);
    const [history, setHistory] = useState<ScanResult[]>([]);
    const [quarantine, setQuarantine] = useState<QuarantinedFile[]>([]);
    const [scanResult, setScanResult] = useState<ScanResult | null>(null);

    useEffect(() => {
        checkBackend();
        const interval = setInterval(checkBackend, 30000);
        return () => clearInterval(interval);
    }, []);

    const checkBackend = async () => {
        const isOnline = await api.healthCheck();
        setOnline(isOnline);
        if (isOnline) {
            try {
                const statsData = await api.getStats();
                setStats(statsData);
            } catch (e) {
                console.log('Failed to fetch stats');
            }
        }
    };

    const loadHistory = async () => {
        setLoading(true);
        try {
            const data = await api.getHistory(50);
            setHistory(data);
        } catch (e) {
            Alert.alert('Error', 'Failed to load history');
        } finally {
            setLoading(false);
        }
    };

    const loadQuarantine = async () => {
        setLoading(true);
        try {
            const data = await api.getQuarantine();
            setQuarantine(data);
        } catch (e) {
            Alert.alert('Error', 'Failed to load quarantine');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (activeTab === 'history') loadHistory();
        if (activeTab === 'quarantine') loadQuarantine();
    }, [activeTab]);

    const handlePickFile = async () => {
        try {
            const result = await DocumentPicker.getDocumentAsync({
                type: '*/*',
                copyToCacheDirectory: true,
            });

            if (result.canceled) return;

            const file = result.assets[0];
            setScanning(true);
            setScanResult(null);

            try {
                const scanRes = await api.scanFile(
                    file.uri,
                    file.name,
                    file.mimeType || 'application/octet-stream'
                );
                setScanResult(scanRes);
            } catch (e) {
                Alert.alert('Scan Failed', 'Could not scan the file. Is the backend running?');
            } finally {
                setScanning(false);
            }
        } catch (e) {
            Alert.alert('Error', 'Failed to pick file');
        }
    };

    const handleSeed = async () => {
        try {
            const result = await api.seedDatabase();
            Alert.alert('Success', result.message);
            checkBackend();
        } catch {
            Alert.alert('Error', 'Failed to seed database');
        }
    };

    const handleDeleteFromQuarantine = async (hash: string) => {
        Alert.alert('Delete File', 'Permanently delete this quarantined file?', [
            { text: 'Cancel', style: 'cancel' },
            {
                text: 'Delete',
                style: 'destructive',
                onPress: async () => {
                    try {
                        await api.deleteFromQuarantine(hash);
                        loadQuarantine();
                    } catch {
                        Alert.alert('Error', 'Failed to delete');
                    }
                }
            }
        ]);
    };

    const handleClearQuarantine = async () => {
        Alert.alert('Clear Quarantine', 'Delete ALL quarantined files?', [
            { text: 'Cancel', style: 'cancel' },
            {
                text: 'Clear All',
                style: 'destructive',
                onPress: async () => {
                    try {
                        await api.clearQuarantine();
                        loadQuarantine();
                    } catch {
                        Alert.alert('Error', 'Failed to clear');
                    }
                }
            }
        ]);
    };

    const formatSize = (bytes: number) => {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    return (
        <View style={styles.container}>
            <StatusBar style="light" />

            {/* Header */}
            <View style={styles.header}>
                <View style={styles.headerContent}>
                    <View style={styles.logo}>
                        <View style={styles.logoIcon}>
                            <Text style={{ fontSize: 20 }}>🛡️</Text>
                        </View>
                        <Text style={styles.logoText}>MalGuard</Text>
                    </View>
                    <View style={styles.statusBadge}>
                        <View style={[styles.statusDot, !online && styles.statusDotOffline]} />
                        <Text style={styles.statusText}>
                            {online ? 'Connected' : 'Offline'}
                        </Text>
                    </View>
                </View>
            </View>

            {/* Content */}
            <ScrollView style={styles.content}>
                {/* Offline Warning */}
                {!online && (
                    <View style={[styles.card, { backgroundColor: colors.dangerBg, borderColor: colors.danger }]}>
                        <Text style={{ color: colors.danger, fontWeight: '500', textAlign: 'center' }}>
                            ⚠️ Backend server is not running
                        </Text>
                    </View>
                )}

                {/* Empty DB Prompt */}
                {online && stats && stats.total_signatures === 0 && (
                    <View style={[styles.card, { backgroundColor: colors.primaryBg, borderColor: colors.primary }]}>
                        <Text style={{ color: colors.primary, textAlign: 'center', marginBottom: 12 }}>
                            📭 No signatures loaded
                        </Text>
                        <TouchableOpacity
                            style={[styles.button, { backgroundColor: colors.primary }]}
                            onPress={handleSeed}
                        >
                            <Text style={styles.buttonText}>🌱 Load Sample Signatures</Text>
                        </TouchableOpacity>
                    </View>
                )}

                {/* Scanner Tab */}
                {activeTab === 'scan' && (
                    <>
                        <View style={styles.card}>
                            <Text style={styles.cardTitle}>🔍 Scan File</Text>
                            <Text style={styles.cardSubtitle}>
                                Select a file to scan for malware
                            </Text>

                            <TouchableOpacity
                                style={[styles.uploadZone, scanning && { opacity: 0.5 }]}
                                onPress={handlePickFile}
                                disabled={scanning || !online}
                            >
                                {scanning ? (
                                    <>
                                        <ActivityIndicator size="large" color={colors.primary} />
                                        <Text style={[styles.uploadTitle, { marginTop: 16 }]}>
                                            Scanning...
                                        </Text>
                                    </>
                                ) : (
                                    <>
                                        <Text style={styles.uploadIcon}>📁</Text>
                                        <Text style={styles.uploadTitle}>Tap to Select File</Text>
                                        <Text style={styles.uploadSubtitle}>
                                            Choose any file to scan
                                        </Text>
                                    </>
                                )}
                            </TouchableOpacity>
                        </View>

                        {/* Scan Result */}
                        {scanResult && (
                            <View style={[
                                styles.card,
                                scanResult.detected && { backgroundColor: colors.dangerBg, borderColor: colors.danger }
                            ]}>
                                <View style={{ flexDirection: 'row', alignItems: 'center', gap: 12 }}>
                                    <View style={[
                                        styles.resultIcon,
                                        { backgroundColor: scanResult.detected ? colors.dangerBg : colors.successBg }
                                    ]}>
                                        <Text style={{ fontSize: 24 }}>
                                            {scanResult.detected ? '🚨' : '✅'}
                                        </Text>
                                    </View>
                                    <View style={{ flex: 1 }}>
                                        <Text style={styles.cardTitle}>
                                            {scanResult.detected ? 'Threat Detected!' : 'File is Clean'}
                                        </Text>
                                        <Text style={[styles.cardSubtitle, { marginBottom: 0 }]}>
                                            {scanResult.file_name}
                                        </Text>
                                    </View>
                                </View>

                                {scanResult.malware_name && (
                                    <View style={{ marginTop: 12, backgroundColor: colors.surface, padding: 12, borderRadius: 8 }}>
                                        <Text style={{ color: colors.danger, fontWeight: '600' }}>
                                            {scanResult.malware_name}
                                        </Text>
                                        <Text style={{ color: colors.textMuted, fontSize: 12, marginTop: 4 }}>
                                            Severity: {scanResult.severity}
                                        </Text>
                                    </View>
                                )}

                                <View style={{ marginTop: 12, gap: 4 }}>
                                    <Text style={{ color: colors.textSecondary, fontSize: 13 }}>
                                        Size: {formatSize(scanResult.file_size)}
                                    </Text>
                                    <Text style={{ color: colors.textSecondary, fontSize: 13 }}>
                                        Reason: {scanResult.reason}
                                    </Text>
                                </View>
                            </View>
                        )}
                    </>
                )}

                {/* History Tab */}
                {activeTab === 'history' && (
                    <View style={styles.card}>
                        <Text style={styles.cardTitle}>📋 Scan History</Text>
                        <Text style={styles.cardSubtitle}>{history.length} entries</Text>

                        {loading ? (
                            <View style={styles.center}>
                                <ActivityIndicator size="large" color={colors.primary} />
                            </View>
                        ) : history.length === 0 ? (
                            <View style={styles.emptyState}>
                                <Text style={styles.emptyIcon}>📋</Text>
                                <Text style={styles.emptyText}>No scan history yet</Text>
                            </View>
                        ) : (
                            history.map((item, index) => (
                                <View
                                    key={`${item.file_name}-${index}`}
                                    style={[styles.resultItem, item.detected && styles.resultItemDetected]}
                                >
                                    <View style={[
                                        styles.resultIcon,
                                        { backgroundColor: item.detected ? colors.dangerBg : colors.successBg }
                                    ]}>
                                        <Text style={{ fontSize: 20 }}>{item.detected ? '🚨' : '✅'}</Text>
                                    </View>
                                    <View style={styles.resultInfo}>
                                        <Text style={styles.resultName} numberOfLines={1}>
                                            {item.file_name}
                                        </Text>
                                        <Text style={styles.resultMeta}>
                                            {formatSize(item.file_size)} • {item.reason}
                                        </Text>
                                        {item.malware_name && (
                                            <Text style={{ color: colors.danger, fontSize: 12, marginTop: 2 }}>
                                                {item.malware_name}
                                            </Text>
                                        )}
                                    </View>
                                </View>
                            ))
                        )}
                    </View>
                )}

                {/* Quarantine Tab */}
                {activeTab === 'quarantine' && (
                    <View style={styles.card}>
                        <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
                            <View>
                                <Text style={styles.cardTitle}>🔒 Quarantine</Text>
                                <Text style={styles.cardSubtitle}>{quarantine.length} isolated files</Text>
                            </View>
                            {quarantine.length > 0 && (
                                <TouchableOpacity
                                    style={[styles.button, { backgroundColor: colors.danger, paddingHorizontal: 12 }]}
                                    onPress={handleClearQuarantine}
                                >
                                    <Text style={styles.buttonText}>Clear All</Text>
                                </TouchableOpacity>
                            )}
                        </View>

                        {loading ? (
                            <View style={styles.center}>
                                <ActivityIndicator size="large" color={colors.primary} />
                            </View>
                        ) : quarantine.length === 0 ? (
                            <View style={styles.emptyState}>
                                <Text style={styles.emptyIcon}>🔒</Text>
                                <Text style={styles.emptyText}>No files in quarantine</Text>
                                <Text style={{ color: colors.textMuted, fontSize: 12, textAlign: 'center' }}>
                                    Detected malware will appear here
                                </Text>
                            </View>
                        ) : (
                            quarantine.map((item, index) => (
                                <View
                                    key={`${item.hash}-${index}`}
                                    style={[styles.resultItem, styles.resultItemDetected]}
                                >
                                    <View style={[styles.resultIcon, { backgroundColor: colors.dangerBg }]}>
                                        <Text style={{ fontSize: 20 }}>🚨</Text>
                                    </View>
                                    <View style={styles.resultInfo}>
                                        <Text style={styles.resultName} numberOfLines={1}>
                                            {item.original_name}
                                        </Text>
                                        <Text style={{ color: colors.danger, fontSize: 12 }}>
                                            {item.malware_name}
                                        </Text>
                                        <Text style={styles.resultMeta}>
                                            {item.severity} • {new Date(item.quarantined_on).toLocaleDateString()}
                                        </Text>
                                    </View>
                                    <TouchableOpacity
                                        style={[styles.button, { backgroundColor: colors.danger, paddingHorizontal: 8, paddingVertical: 6 }]}
                                        onPress={() => handleDeleteFromQuarantine(item.hash)}
                                    >
                                        <Text style={{ color: '#fff', fontSize: 12 }}>🗑️</Text>
                                    </TouchableOpacity>
                                </View>
                            ))
                        )}
                    </View>
                )}

                {/* Stats Tab */}
                {activeTab === 'stats' && (
                    <View style={styles.card}>
                        <Text style={styles.cardTitle}>📊 Statistics</Text>
                        <Text style={styles.cardSubtitle}>Overview of your scans</Text>

                        {stats ? (
                            <View style={styles.statsGrid}>
                                <View style={styles.statCard}>
                                    <Text style={styles.statValue}>{stats.total_signatures}</Text>
                                    <Text style={styles.statLabel}>Signatures</Text>
                                </View>
                                <View style={styles.statCard}>
                                    <Text style={styles.statValue}>{stats.total_scans}</Text>
                                    <Text style={styles.statLabel}>Total Scans</Text>
                                </View>
                                <View style={styles.statCard}>
                                    <Text style={[styles.statValue, { color: colors.danger }]}>
                                        {stats.total_detections}
                                    </Text>
                                    <Text style={styles.statLabel}>Detections</Text>
                                </View>
                                <View style={styles.statCard}>
                                    <Text style={[styles.statValue, { color: colors.success }]}>
                                        {stats.total_scans - stats.total_detections}
                                    </Text>
                                    <Text style={styles.statLabel}>Clean</Text>
                                </View>
                            </View>
                        ) : (
                            <View style={styles.emptyState}>
                                <Text style={styles.emptyText}>
                                    {online ? 'Loading stats...' : 'Connect to backend to view stats'}
                                </Text>
                            </View>
                        )}
                    </View>
                )}
            </ScrollView>

            {/* Tab Bar */}
            <View style={styles.tabBar}>
                <TouchableOpacity
                    style={[styles.tab, activeTab === 'scan' && styles.tabActive]}
                    onPress={() => setActiveTab('scan')}
                >
                    <Text style={styles.tabIcon}>🔍</Text>
                    <Text style={[styles.tabLabel, activeTab === 'scan' && styles.tabLabelActive]}>
                        Scan
                    </Text>
                </TouchableOpacity>
                <TouchableOpacity
                    style={[styles.tab, activeTab === 'history' && styles.tabActive]}
                    onPress={() => setActiveTab('history')}
                >
                    <Text style={styles.tabIcon}>📋</Text>
                    <Text style={[styles.tabLabel, activeTab === 'history' && styles.tabLabelActive]}>
                        History
                    </Text>
                </TouchableOpacity>
                <TouchableOpacity
                    style={[styles.tab, activeTab === 'quarantine' && styles.tabActive]}
                    onPress={() => setActiveTab('quarantine')}
                >
                    <Text style={styles.tabIcon}>🔒</Text>
                    <Text style={[styles.tabLabel, activeTab === 'quarantine' && styles.tabLabelActive]}>
                        Quarantine
                    </Text>
                </TouchableOpacity>
                <TouchableOpacity
                    style={[styles.tab, activeTab === 'stats' && styles.tabActive]}
                    onPress={() => setActiveTab('stats')}
                >
                    <Text style={styles.tabIcon}>📊</Text>
                    <Text style={[styles.tabLabel, activeTab === 'stats' && styles.tabLabelActive]}>
                        Stats
                    </Text>
                </TouchableOpacity>
            </View>
        </View>
    );
}
