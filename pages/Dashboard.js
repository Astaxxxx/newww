import React, { useState, useEffect } from 'react';
import '../App.css';

const Dashboard = ({ user }) => {
  const [performanceData, setPerformanceData] = useState([]);
  const [recentSessions, setRecentSessions] = useState([]);
  const [deviceStats, setDeviceStats] = useState([]);
  const [timeRange, setTimeRange] = useState('day');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadDashboardData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // Get performance metrics
        const token = localStorage.getItem('authToken');
        const headers = {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        };
        
        // Fetch performance data
        const performanceResponse = await fetch(
          `http://localhost:5000/api/analytics/performance?timeRange=${timeRange}`,
          { headers }
        );
        
        if (!performanceResponse.ok) {
          throw new Error('Failed to load performance data');
        }
        
        const performanceData = await performanceResponse.json();
        setPerformanceData(performanceData.data);
        
        // Fetch recent sessions
        const sessionsResponse = await fetch(
          'http://localhost:5000/api/sessions/recent',
          { headers }
        );
        
        if (!sessionsResponse.ok) {
          throw new Error('Failed to load recent sessions');
        }
        
        const sessionsData = await sessionsResponse.json();
        setRecentSessions(sessionsData.sessions);
        
        // Fetch device statistics
        const devicesResponse = await fetch(
          'http://localhost:5000/api/devices/stats',
          { headers }
        );
        
        if (!devicesResponse.ok) {
          throw new Error('Failed to load device statistics');
        }
        
        const devicesData = await devicesResponse.json();
        setDeviceStats(devicesData.devices);
        
      } catch (err) {
        console.error('Dashboard data loading error:', err);
        setError('Failed to load dashboard data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, [timeRange]);

  // Calculate averages
  const calculateAverage = (data, field) => {
    if (!data || data.length === 0) return 0;
    const sum = data.reduce((total, item) => total + (item[field] || 0), 0);
    return Math.round(sum / data.length);
  };

  const avgAPM = calculateAverage(performanceData, 'actions_per_minute');
  const avgKeyPresses = calculateAverage(performanceData, 'key_press_count');
  const avgMouseClicks = calculateAverage(performanceData, 'mouse_click_count');

  // Format date for display
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  if (loading) {
    return <div className="loading">Loading dashboard data...</div>;
  }

  if (error) {
    return (
      <div className="card" style={{ color: 'var(--error-color)' }}>
        <h2>Error</h2>
        <p>{error}</p>
        <button 
          className="btn btn-primary" 
          onClick={() => window.location.reload()}
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <h1>Performance Dashboard</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <button 
          className={`btn ${timeRange === 'day' ? 'btn-primary' : ''}`}
          onClick={() => setTimeRange('day')}
          style={{ marginRight: '10px' }}
        >
          Today
        </button>
        <button 
          className={`btn ${timeRange === 'week' ? 'btn-primary' : ''}`}
          onClick={() => setTimeRange('week')}
          style={{ marginRight: '10px' }}
        >
          This Week
        </button>
        <button 
          className={`btn ${timeRange === 'month' ? 'btn-primary' : ''}`}
          onClick={() => setTimeRange('month')}
        >
          This Month
        </button>
      </div>

      <div className="card" style={{ marginBottom: '20px' }}>
        <h2 className="card-title">Performance Summary</h2>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '20px' }}>
          <div style={{ flex: '1', minWidth: '150px' }}>
            <h3>Average APM</h3>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: '5px 0' }}>{avgAPM}</p>
          </div>
          <div style={{ flex: '1', minWidth: '150px' }}>
            <h3>Avg Key Presses</h3>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: '5px 0' }}>{avgKeyPresses}</p>
          </div>
          <div style={{ flex: '1', minWidth: '150px' }}>
            <h3>Avg Mouse Clicks</h3>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: '5px 0' }}>{avgMouseClicks}</p>
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="card-title">APM Over Time</h2>
        <div>
          {/* In a real implementation, we would use a chart library like Recharts */}
          <p>Chart visualization would go here. Using mock data for demonstration.</p>
          <div style={{ 
            display: 'flex', 
            height: '200px', 
            alignItems: 'flex-end',
            gap: '5px',
            padding: '20px 0'
          }}>
            {performanceData.map((data, index) => (
              <div 
                key={index} 
                style={{
                  height: `${data.actions_per_minute / 2}px`,
                  width: '30px',
                  backgroundColor: 'var(--primary-color)',
                  borderRadius: '4px 4px 0 0',
                  flex: '1'
                }}
                title={`${formatDate(data.timestamp)}: ${data.actions_per_minute} APM`}
              />
            ))}
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '20px', marginTop: '20px', flexWrap: 'wrap' }}>
        <div className="card" style={{ flex: '2', minWidth: '300px' }}>
          <h2 className="card-title">Recent Sessions</h2>
          {recentSessions.length > 0 ? (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <th style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid var(--border-color)' }}>Date</th>
                  <th style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid var(--border-color)' }}>Duration</th>
                  <th style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid var(--border-color)' }}>Avg APM</th>
                  <th style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid var(--border-color)' }}>Device</th>
                </tr>
              </thead>
              <tbody>
                {recentSessions.map(session => (
                  <tr key={session.id}>
                    <td style={{ padding: '8px', borderBottom: '1px solid var(--border-color)' }}>{formatDate(session.start_time)}</td>
                    <td style={{ padding: '8px', borderBottom: '1px solid var(--border-color)' }}>{session.duration_minutes} min</td>
                    <td style={{ padding: '8px', borderBottom: '1px solid var(--border-color)' }}>{session.average_apm}</td>
                    <td style={{ padding: '8px', borderBottom: '1px solid var(--border-color)' }}>{session.device_name}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p>No recent sessions found.</p>
          )}
        </div>

        <div className="card" style={{ flex: '1', minWidth: '300px' }}>
          <h2 className="card-title">Device Usage</h2>
          {deviceStats.length > 0 ? (
            <div>
              {deviceStats.map((device, index) => (
                <div key={index} style={{ marginBottom: '15px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>{device.device_name}</span>
                    <span>{Math.round(device.usage_percentage * 100)}%</span>
                  </div>
                  <div style={{ 
                    height: '10px', 
                    backgroundColor: 'var(--bg-color)', 
                    borderRadius: '5px',
                    margin: '5px 0'
                  }}>
                    <div style={{ 
                      height: '100%', 
                      width: `${device.usage_percentage * 100}%`,
                      backgroundColor: 'var(--primary-color)',
                      borderRadius: '5px'
                    }} />
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem' }}>
                    <span>Avg APM: {device.average_apm}</span>
                    <span>Sessions: {device.total_sessions}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p>No device statistics available.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;