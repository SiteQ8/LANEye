import React from 'react';

interface DashboardProps {
  totalHosts: number;
  onlineHosts: number;
  offlineHosts: number;
  scanCount: number;
  onScan: () => void;
  scanning: boolean;
}

const Dashboard: React.FC<DashboardProps> = ({
  totalHosts, onlineHosts, offlineHosts, scanCount, onScan, scanning
}) => {
  return (
    <div className="dashboard">
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Hosts</h3>
          <div className="value">{totalHosts}</div>
        </div>
        <div className="stat-card">
          <h3>Online</h3>
          <div className="value online">{onlineHosts}</div>
        </div>
        <div className="stat-card">
          <h3>Offline</h3>
          <div className="value offline">{offlineHosts}</div>
        </div>
        <div className="stat-card">
          <h3>Scans</h3>
          <div className="value">{scanCount}</div>
        </div>
      </div>
      <button onClick={onScan} disabled={scanning}>
        {scanning ? 'Scanning...' : 'Scan Network'}
      </button>
    </div>
  );
};

export default Dashboard;
