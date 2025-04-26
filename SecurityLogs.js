import React, { useState, useEffect } from 'react';
import '../App.css';

const SecurityLogs = ({ user }) => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all'); // 'all', 'warning', 'critical'

  useEffect(() => {
    // Only admin users should access this page
    if (user.role !== 'admin') {
      setError('Access denied. Admin privileges required.');
      setLoading(false);
      return;
    }

    const fetchSecurityLogs = async () => {
      setLoading(true);
      try {
        const token = localStorage.getItem('authToken');
        const response = await fetch(`http://localhost:5000/api/security/logs?severity=${filter}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (!response.ok) {
          throw new Error(
            response.status === 403 
              ? 'Access denied. Admin privileges required.'
              : 'Failed to fetch security logs'
          );
        }

        const data = await response.json();
        setLogs(data.logs || []);
      } catch (err) {
        console.error('Error fetching security logs:', err);
        setError(err.message || 'Failed to load security logs. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchSecurityLogs();
  }, [user, filter]);

  // Format date for display
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  // Get severity color
  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical':
        return 'var(--error-color)';
      case 'warning':
        return '#ff9800';
      default:
        return 'var(--text-color)';
    }
  };

  // Get event icon
  const getEventIcon = (eventType) => {
    if (eventType.includes('auth')) return '🔑';
    if (eventType.includes('data')) return '📊';
    if (eventType.includes('login')) return '👤';
    if (eventType.includes('access')) return '🚫';
    if (eventType.includes('device')) return '💻';
    return '🔔';
  };

  if (loading) {
    return <div className="loading">Loading security logs...</div>;
  }

  if (error) {
    return (
      <div className="card" style={{ color: 'var(--error-color)' }}>
        <h2>Error</h2>
        <p>{error}</p>
        {error.includes('Access denied') ? (
          <p>You need admin privileges to view security logs.</p>
        ) : (
          <button 
            className="btn btn-primary" 
            onClick={() => window.location.reload()}
          >
            Retry
          </button>
        )}
      </div>
    );
  }

  return (
    <div>
      <h1>Security Audit Logs</h1>
      <p>Monitor and review security events</p>

      <div style={{ marginBottom: '20px' }}>
        <button 
          className={`btn ${filter === 'all' ? 'btn-primary' : ''}`}
          onClick={() => setFilter('all')}
          style={{ marginRight: '10px' }}
        >
          All Events
        </button>
        <button 
          className={`btn ${filter === 'warning' ? 'btn-primary' : ''}`}
          onClick={() => setFilter('warning')}
          style={{ marginRight: '10px' }}
        >
          Warnings
        </button>
        <button 
          className={`btn ${filter === 'critical' ? 'btn-primary' : ''}`}
          onClick={() => setFilter('critical')}
        >
          Critical
        </button>
      </div>

      <div className="card">
        <h2 className="card-title">Security Events</h2>
        {logs.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <th style={{ textAlign: 'left', padding: '12px 8px', borderBottom: '2px solid var(--border-color)' }}>Timestamp</th>
                  <th style={{ textAlign: 'left', padding: '12px 8px', borderBottom: '2px solid var(--border-color)' }}>Event Type</th>
                  <th style={{ textAlign: 'left', padding: '12px 8px', borderBottom: '2px solid var(--border-color)' }}>Severity</th>
                  <th style={{ textAlign: 'left', padding: '12px 8px', borderBottom: '2px solid var(--border-color)' }}>IP Address</th>
                  <th style={{ textAlign: 'left', padding: '12px 8px', borderBottom: '2px solid var(--border-color)' }}>Details</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log, index) => (
                  <tr key={index}>
                    <td style={{ padding: '12px 8px', borderBottom: '1px solid var(--border-color)' }}>
                      {formatDate(log.timestamp)}
                    </td>
                    <td style={{ padding: '12px 8px', borderBottom: '1px solid var(--border-color)' }}>
                      <div style={{ display: 'flex', alignItems: 'center' }}>
                        <span style={{ marginRight: '8px', fontSize: '1.2rem' }}>{getEventIcon(log.event_type)}</span>
                        {log.event_type}
                      </div>
                    </td>
                    <td style={{ padding: '12px 8px', borderBottom: '1px solid var(--border-color)' }}>
                      <span style={{ 
                        display: 'inline-block',
                        padding: '4px 8px',
                        borderRadius: '4px',
                        backgroundColor: getSeverityColor(log.severity),
                        color: 'white',
                        fontWeight: 'bold',
                        fontSize: '0.8rem',
                        textTransform: 'uppercase'
                      }}>
                        {log.severity}
                      </span>
                    </td>
                    <td style={{ padding: '12px 8px', borderBottom: '1px solid var(--border-color)' }}>
                      {log.ip_address || '-'}
                    </td>
                    <td style={{ padding: '12px 8px', borderBottom: '1px solid var(--border-color)' }}>
                      <div style={{
                        maxWidth: '300px',
                        whiteSpace: 'nowrap',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis'
                      }}>
                        {typeof log.details === 'object' 
                          ? JSON.stringify(log.details) 
                          : log.details || 'No details available'}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '20px' }}>
            <p>No security events found for the selected filter.</p>
          </div>
        )}
      </div>

      <div className="card">
        <h2 className="card-title">Security Dashboard</h2>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '20px' }}>
          <div style={{ 
            flex: '1',
            minWidth: '200px',
            padding: '15px',
            borderRadius: '8px',
            backgroundColor: 'rgba(0, 200, 83, 0.1)',
            border: '1px solid var(--success-color)'
          }}>
            <h3 style={{ margin: '0 0 10px 0', color: 'var(--success-color)' }}>System Status</h3>
            <p style={{ margin: '0', fontWeight: 'bold', color: 'var(--success-color)' }}>SECURE</p>
            <p style={{ margin: '5px 0 0 0', fontSize: '0.9rem' }}>All security controls active</p>
          </div>
          
          <div style={{ 
            flex: '1',
            minWidth: '200px',
            padding: '15px',
            borderRadius: '8px',
            backgroundColor: 'rgba(98, 0, 234, 0.1)',
            border: '1px solid var(--primary-color)'
          }}>
            <h3 style={{ margin: '0 0 10px 0', color: 'var(--primary-color)' }}>Active Devices</h3>
            <p style={{ margin: '0', fontWeight: 'bold', fontSize: '1.5rem' }}>2</p>
            <p style={{ margin: '5px 0 0 0', fontSize: '0.9rem' }}>All devices authenticated</p>
          </div>
          
          <div style={{ 
            flex: '1',
            minWidth: '200px',
            padding: '15px',
            borderRadius: '8px',
            backgroundColor: filter === 'critical' ? 'rgba(176, 0, 32, 0.1)' : 'rgba(255, 152, 0, 0.1)',
            border: `1px solid ${filter === 'critical' ? 'var(--error-color)' : '#ff9800'}`
          }}>
            <h3 style={{ margin: '0 0 10px 0', color: filter === 'critical' ? 'var(--error-color)' : '#ff9800' }}>
              Security Events
            </h3>
            <p style={{ margin: '0', fontWeight: 'bold', fontSize: '1.5rem' }}>{logs.length}</p>
            <p style={{ margin: '5px 0 0 0', fontSize: '0.9rem' }}>
              Last 24 hours
            </p>
          </div>
        </div>
        
        <div style={{ marginTop: '20px' }}>
          <h3>Security Recommendations</h3>
          <ul>
            <li>Review failed authentication attempts</li>
            <li>Verify all registered devices</li>
            <li>Consider enabling multi-factor authentication</li>
            <li>Rotate encryption keys every 90 days</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default SecurityLogs;