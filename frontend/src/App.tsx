import React, { useState, useEffect } from 'react';

interface Host {
  ip: string;
  mac: string;
  vendor: string;
  hostname: string | null;
  status: 'online' | 'offline';
  method: string;
  last_seen: string;
  response_time_ms: number;
}

interface Stats {
  total_hosts: number;
  online_hosts: number;
  offline_hosts: number;
  last_scan: string | null;
  scan_count: number;
}

const App: React.FC = () => {
  const [hosts, setHosts] = useState<Host[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [scanning, setScanning] = useState(false);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState<'dashboard' | 'hosts'>('dashboard');

  const apiBase = window.location.origin;

  const fetchHosts = async () => {
    try {
      const res = await fetch(`${apiBase}/api/hosts`);
      const data = await res.json();
      setHosts(data);
    } catch (err) {
      console.error('Failed to fetch hosts:', err);
    }
  };

  const fetchStats = async () => {
    try {
      const res = await fetch(`${apiBase}/api/stats`);
      const data = await res.json();
      setStats(data);
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  };

  const triggerScan = async () => {
    setScanning(true);
    try {
      await fetch(`${apiBase}/api/scan`, { method: 'POST' });
      await fetchHosts();
      await fetchStats();
    } catch (err) {
      console.error('Scan failed:', err);
    }
    setScanning(false);
  };

  useEffect(() => {
    fetchHosts();
    fetchStats();
    const interval = setInterval(() => {
      fetchHosts();
      fetchStats();
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  const filtered = hosts.filter(h =>
    h.ip.includes(search) ||
    h.mac.toLowerCase().includes(search.toLowerCase()) ||
    h.vendor.toLowerCase().includes(search.toLowerCase()) ||
    (h.hostname || '').toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="app">
      <h1>🔍 LANEye</h1>
      <p>Network Scanner v1.1.0</p>
      <button onClick={triggerScan} disabled={scanning}>
        {scanning ? 'Scanning...' : 'Scan Now'}
      </button>
      {stats && (
        <div className="stats">
          <span>Total: {stats.total_hosts}</span>
          <span>Online: {stats.online_hosts}</span>
          <span>Offline: {stats.offline_hosts}</span>
          <span>Scans: {stats.scan_count}</span>
        </div>
      )}
      <input
        type="text"
        placeholder="Search hosts..."
        value={search}
        onChange={e => setSearch(e.target.value)}
      />
      <table>
        <thead>
          <tr>
            <th>Status</th><th>IP</th><th>MAC</th>
            <th>Vendor</th><th>Hostname</th><th>Response</th>
          </tr>
        </thead>
        <tbody>
          {filtered.map(h => (
            <tr key={h.ip}>
              <td>{h.status === 'online' ? '🟢' : '🔴'}</td>
              <td>{h.ip}</td>
              <td>{h.mac}</td>
              <td>{h.vendor}</td>
              <td>{h.hostname || '—'}</td>
              <td>{h.response_time_ms ? `${h.response_time_ms}ms` : '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default App;
