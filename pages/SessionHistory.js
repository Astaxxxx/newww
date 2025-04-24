import React, { useState, useEffect } from 'react';
import '../App.css';

const SessionHistory = ({ user }) => {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all'); // 'all', 'week', 'month'

  useEffect(() => {
    const fetchSessions = async () => {
      setLoading(true);
      try {
        const token = localStorage.getItem('authToken');
        const response = await fetch(`http://localhost:5000/api/sessions/recent?filter=${filter}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (!response.ok) {
          throw new Error('Failed to fetch sessions');
        }

        const data = await response.json();
        setSessions(data.sessions);
      } catch (err) {
        console.error('Error fetching sessions:', err);
        setError('Failed to load session history. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchSessions();
  }, [filter]);

  // Format date for display
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  // Calculate average from sample data for demo
  const calculateAverage = (session) => {
    // In real implementation, this would be fetched from the server
    return session.average_apm;
  };

  if (loading) {
    return <div className="loading">Loading session history...</div>;
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
    <div>
      <h1>Session History</h1>
      <p>View and analyze your past gaming sessions</p>

      <div style={{ marginBottom: '20px' }}>
        <button 
          className={`btn ${filter === 'all' ? 'btn-primary' : ''}`}
          onClick={() => setFilter('all')}
          style={{ marginRight: '10px' }}
        >
          All Time
        </button>
        <button 
          className={`btn ${filter === 'week' ? 'btn-primary' : ''}`}
          onClick={() => setFilter('week')}
          style={{ marginRight: '10px' }}
        >
          This Week
        </button>
        <button 
          className={`btn ${filter === 'month' ? 'btn-primary' : ''}`}
          onClick={() => setFilter('month')}
        >
          This Month
        </button>
      </div>

      <div className="card">
        <h2 className="card-title">Your Gaming Sessions</h2>
        {sessions.length > 0 ? (
          <div>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <th style={{ textAlign: 'left', padding: '12px 8px', borderBottom: '2px solid var(--border-color)' }}>Date</th>
                  <th style={{ textAlign: 'left', padding: '12px 8px', borderBottom: '2px solid var(--border-color)' }}>Duration</th>
                  <th style={{ textAlign: 'left', padding: '12px 8px', borderBottom: '2px solid var(--border-color)' }}>Avg APM</th>
                  <th style={{ textAlign: 'left', padding: '12px 8px', borderBottom: '2px solid var(--border-color)' }}>Device</th>
                  <th style={{ textAlign: 'left', padding: '12px 8px', borderBottom: '2px solid var(--border-color)' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {sessions.map(session => (
                  <tr key={session.id}>
                    <td style={{ padding: '12px 8px', borderBottom: '1px solid var(--border-color)' }}>
                      {formatDate(session.start_time)}
                    </td>
                    <td style={{ padding: '12px 8px', borderBottom: '1px solid var(--border-color)' }}>
                      {session.duration_minutes} min
                    </td>
                    <td style={{ padding: '12px 8px', borderBottom: '1px solid var(--border-color)' }}>
                      <div style={{ display: 'flex', alignItems: 'center' }}>
                        <span style={{ marginRight: '10px' }}>{calculateAverage(session)}</span>
                        <div style={{ 
                          height: '8px', 
                          width: '60px', 
                          backgroundColor: 'var(--bg-color)', 
                          borderRadius: '4px' 
                        }}>
                          <div style={{ 
                            height: '100%', 
                            width: `${Math.min(100, (calculateAverage(session) / 2))}%`, 
                            backgroundColor: 'var(--primary-color)', 
                            borderRadius: '4px' 
                          }} />
                        </div>
                      </div>
                    </td>
                    <td style={{ padding: '12px 8px', borderBottom: '1px solid var(--border-color)' }}>
                      {session.device_name}
                    </td>
                    <td style={{ padding: '12px 8px', borderBottom: '1px solid var(--border-color)' }}>
                      <button 
                        className="btn"
                        style={{ padding: '6px 12px', fontSize: '0.8rem' }}
                        onClick={() => alert(`Session details would open here for session ${session.id}`)}
                      >
                        Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '20px' }}>
            <p>No sessions found for the selected time period.</p>
            <p>Start the agent while gaming to record your sessions.</p>
          </div>
        )}
      </div>

      <div className="card">
        <h2 className="card-title">Performance Analysis</h2>
        <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
          <div style={{ flex: '1', minWidth: '250px' }}>
            <h3>APM Trends</h3>
            <div style={{ 
              height: '160px', 
              backgroundColor: 'var(--card-bg)', 
              border: '1px solid var(--border-color)',
              borderRadius: '8px',
              padding: '10px',
              display: 'flex',
              alignItems: 'flex-end',
              justifyContent: 'space-around',
              gap: '10px'
            }}>
              {/* Simple chart visualization for demo */}
              {[120, 135, 128, 142, 138, 145, 132].map((value, index) => (
                <div 
                  key={index}
                  style={{
                    height: `${value / 1.5}px`,
                    width: '8%',
                    backgroundColor: 'var(--primary-color)',
                    borderRadius: '4px 4px 0 0',
                    position: 'relative'
                  }}
                >
                  <span style={{ 
                    position: 'absolute', 
                    top: '-20px', 
                    left: '50%', 
                    transform: 'translateX(-50%)',
                    fontSize: '0.7rem'
                  }}>
                    {value}
                  </span>
                </div>
              ))}
            </div>
          </div>
          <div style={{ flex: '1', minWidth: '250px' }}>
            <h3>Session Duration</h3>
            <div style={{ 
              height: '160px', 
              backgroundColor: 'var(--card-bg)', 
              border: '1px solid var(--border-color)',
              borderRadius: '8px',
              padding: '10px',
              display: 'flex',
              alignItems: 'flex-end',
              justifyContent: 'space-around',
              gap: '10px'
            }}>
              {/* Simple chart visualization for demo */}
              {[60, 75, 90, 120, 80, 100, 110].map((value, index) => (
                <div 
                  key={index}
                  style={{
                    height: `${value / 1}px`,
                    width: '8%',
                    backgroundColor: 'var(--secondary-color)',
                    borderRadius: '4px 4px 0 0',
                    position: 'relative'
                  }}
                >
                  <span style={{ 
                    position: 'absolute', 
                    top: '-20px', 
                    left: '50%', 
                    transform: 'translateX(-50%)',
                    fontSize: '0.7rem'
                  }}>
                    {value}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
        <div style={{ marginTop: '20px' }}>
          <h3>Performance Insights</h3>
          <ul>
            <li>Your highest APM was 145, achieved during your most recent session.</li>
            <li>Your average session duration is 90.7 minutes.</li>
            <li>Your performance is most consistent during evening sessions.</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default SessionHistory;