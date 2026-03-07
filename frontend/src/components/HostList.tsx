import React, { useState } from 'react';

interface Host {
  ip: string;
  mac: string;
  vendor: string;
  hostname: string | null;
  status: string;
  response_time_ms: number;
  last_seen: string;
}

interface HostListProps {
  hosts: Host[];
}

const HostList: React.FC<HostListProps> = ({ hosts }) => {
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState<'ip' | 'vendor' | 'status'>('ip');

  const filtered = hosts
    .filter(h =>
      h.ip.includes(search) ||
      h.mac.toLowerCase().includes(search.toLowerCase()) ||
      h.vendor.toLowerCase().includes(search.toLowerCase()) ||
      (h.hostname || '').toLowerCase().includes(search.toLowerCase())
    )
    .sort((a, b) => {
      if (sortBy === 'ip') {
        return a.ip.localeCompare(b.ip, undefined, { numeric: true });
      }
      return (a[sortBy] || '').localeCompare(b[sortBy] || '');
    });

  return (
    <div className="host-list">
      <input
        type="text"
        placeholder="Search by IP, MAC, vendor, hostname..."
        value={search}
        onChange={e => setSearch(e.target.value)}
      />
      <table>
        <thead>
          <tr>
            <th>Status</th>
            <th onClick={() => setSortBy('ip')} style={{ cursor: 'pointer' }}>IP Address</th>
            <th>MAC Address</th>
            <th onClick={() => setSortBy('vendor')} style={{ cursor: 'pointer' }}>Vendor</th>
            <th>Hostname</th>
            <th>Response</th>
            <th>Last Seen</th>
          </tr>
        </thead>
        <tbody>
          {filtered.map(host => (
            <tr key={host.ip}>
              <td>{host.status === 'online' ? '🟢' : '🔴'} {host.status}</td>
              <td><code>{host.ip}</code></td>
              <td><code>{host.mac}</code></td>
              <td>{host.vendor}</td>
              <td>{host.hostname || '—'}</td>
              <td>{host.response_time_ms ? `${host.response_time_ms}ms` : '—'}</td>
              <td>{host.last_seen}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p>{filtered.length} of {hosts.length} hosts shown</p>
    </div>
  );
};

export default HostList;
