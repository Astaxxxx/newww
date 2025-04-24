// dashboard/src/pages/IoTDevices.js
import React, { useState, useEffect } from 'react';
import '../App.css';

const IoTDevices = ({ user }) => {
  const [devices, setDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [deviceData, setDeviceData] = useState([]);
  const [securityAlerts, setSecurityAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshInterval, setRefreshInterval] = useState(5); // in seconds
  const [isRefreshing, setIsRefreshing] = useState(true);

  useEffect(() => {
    // Load devices from API
    const fetchDevices = async () => {
      try {
        const token = localStorage.getItem('authToken');
        const response = await fetch('http://localhost:5000/api/devices', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (!response.ok) {
          throw new Error('Failed to fetch devices');
        }

        const data = await response.json();
        // Filter IoT devices
        const iotDevices = data.devices.filter(device => 
          device.device_type === 'mouse' || 
          device.device_type === 'keyboard' || 
          device.device_type === 'headset'
        );
        
        setDevices(iotDevices);
        
        // Select first device by default
        if (iotDevices.length > 0 && !selectedDevice) {
          setSelectedDevice(iotDevices[0].client_id);
        }
      } catch (err) {
        console.error('Error fetching devices:', err);
        setError('Failed to load devices. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchDevices();
    
    // Poll for devices every 30 seconds
    const deviceInterval = setInterval(fetchDevices, 30000);
    
    return () => clearInterval(deviceInterval);
  }, [selectedDevice]);

  useEffect(() => {
    // Set up the data refresh interval
    let dataInterval;
    
    if (isRefreshing && selectedDevice) {
      const fetchData = async () => {
        try {
          await Promise.all([
            fetchDeviceData(selectedDevice),
            fetchSecurityAlerts(selectedDevice)
          ]);
        } catch (err) {
          console.error('Error refreshing data:', err);
        }
      };
      
      // Fetch immediately
      fetchData();
      
      // Then set interval
      dataInterval = setInterval(fetchData, refreshInterval * 1000);
    }
    
    return () => {
      if (dataInterval) clearInterval(dataInterval);
    };
  }, [selectedDevice, refreshInterval, isRefreshing]);

  const fetchDeviceData = async (deviceId) => {
    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch(`http://localhost:5000/api/metrics/iot_data/${deviceId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch device data');
      }

      const data = await response.json();
      setDeviceData(data.data || []);
    } catch (err) {
      console.error('Error fetching device data:', err);
    }
  };

  const fetchSecurityAlerts = async (deviceId) => {
    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch(`http://localhost:5000/api/security/device_alerts/${deviceId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch security alerts');
      }

      const data = await response.json();
      setSecurityAlerts(data.alerts || []);
    } catch (err) {
      console.error('Error fetching security alerts:', err);
    }
  };

  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleString();
    } catch (e) {
      return dateString;
    }
  };

  const getMostRecentData = () => {
    if (!deviceData || deviceData.length === 0) return null;
    return deviceData[deviceData.length - 1];
  };

  const getLatestMetrics = () => {
    const recent = getMostRecentData();
    if (!recent || !recent.metrics) return null;
    return recent.metrics;
  };

  const getDeviceStatus = () => {
    const recent = getMostRecentData();
    if (!recent || !recent.status) return { under_attack: false };
    return recent.status;
  };

  const renderDeviceStatus = () => {
    const status = getDeviceStatus();
    const isAttacked = status && status.under_attack;
    
    return (
      <div style={{
        padding: '15px',
        borderRadius: '8px',
        backgroundColor: isAttacked ? 'rgba(176, 0, 32, 0.1)' : 'rgba(0, 200, 83, 0.1)',
        border: `1px solid ${isAttacked ? 'var(--error-color)' : 'var(--success-color)'}`,
        marginBottom: '20px'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div>
            <h3 style={{ margin: '0 0 10px 0' }}>Device Status</h3>
            <p style={{ 
              margin: '0', 
              fontWeight: 'bold',
              color: isAttacked ? 'var(--error-color)' : 'var(--success-color)'
            }}>
              {isAttacked ? 'UNDER ATTACK' : 'SECURE'}
            </p>
          </div>
          <div style={{
            fontSize: '2rem',
            color: isAttacked ? 'var(--error-color)' : 'var(--success-color)'
          }}>
            {isAttacked ? '⚠️' : '✓'}
          </div>
        </div>
        
        {isAttacked && (
          <div style={{ marginTop: '10px' }}>
            <p style={{ margin: '0', fontSize: '0.9rem' }}>
              Attack duration: {status.attack_duration || 0} seconds
            </p>
            <p style={{ margin: '5px 0 0 0', fontSize: '0.9rem' }}>
              Take immediate action to mitigate this attack!
            </p>
          </div>
        )}
      </div>
    );
  };

  const renderDeviceMetrics = () => {
    const metrics = getLatestMetrics();
    if (!metrics) return <p>No metrics available</p>;
    
    return (
      <div className="card">
        <h2 className="card-title">Real-Time Performance Metrics</h2>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '20px' }}>
          {Object.entries(metrics).map(([key, value]) => (
            <div key={key} style={{ flex: '1', minWidth: '150px' }}>
              <h3>{key.replace(/_/g, ' ').toUpperCase()}</h3>
              <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: '5px 0' }}>
                {value}
              </p>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderSecurityAlerts = () => {
    if (!securityAlerts || securityAlerts.length === 0) {
      return (
        <div className="card">
          <h2 className="card-title">Security Alerts</h2>
          <p>No security alerts detected</p>
        </div>
      );
    }
    
    return (
      <div className="card">
        <h2 className="card-title">Security Alerts</h2>
        <div style={{ overflowY: 'auto', maxHeight: '300px' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={{ textAlign: 'left', padding: '12px 8px', position: 'sticky', top: 0, backgroundColor: 'var(--card-bg)', borderBottom: '2px solid var(--border-color)' }}>Timestamp</th>
                <th style={{ textAlign: 'left', padding: '12px 8px', position: 'sticky', top: 0, backgroundColor: 'var(--card-bg)', borderBottom: '2px solid var(--border-color)' }}>Event Type</th>
                <th style={{ textAlign: 'left', padding: '12px 8px', position: 'sticky', top: 0, backgroundColor: 'var(--card-bg)', borderBottom: '2px solid var(--border-color)' }}>Severity</th>
                <th style={{ textAlign: 'left', padding: '12px 8px', position: 'sticky', top: 0, backgroundColor: 'var(--card-bg)', borderBottom: '2px solid var(--border-color)' }}>Details</th>
              </tr>
            </thead>
            <tbody>
              {securityAlerts.slice().reverse().map((alert, index) => (
                <tr key={index}>
                  <td style={{ padding: '12px 8px', borderBottom: '1px solid var(--border-color)' }}>
                    {formatDate(alert.timestamp)}
                  </td>
                  <td style={{ padding: '12px 8px', borderBottom: '1px solid var(--border-color)' }}>
                    {alert.event_type.replace(/_/g, ' ')}
                  </td>
                  <td style={{ padding: '12px 8px', borderBottom: '1px solid var(--border-color)' }}>
                    <span style={{ 
                      display: 'inline-block',
                      padding: '4px 8px',
                      borderRadius: '4px',
                      backgroundColor: alert.severity === 'critical' ? 'var(--error-color)' : '#ff9800',
                      color: 'white',
                      fontWeight: 'bold',
                      fontSize: '0.8rem'
                    }}>
                      {alert.severity.toUpperCase()}
                    </span>
                  </td>
                  <td style={{ padding: '12px 8px', borderBottom: '1px solid var(--border-color)' }}>
                    {alert.details ? JSON.stringify(alert.details) : 'No details'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  if (loading) {
    return <div className="loading">Loading IoT devices...</div>;
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
      <h1>IoT Device Monitoring</h1>
      <p>Monitor your IoT gaming equipment performance and security</p>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <select 
            value={selectedDevice || ''}
            onChange={(e) => setSelectedDevice(e.target.value)}
            className="form-control"
            style={{ padding: '8px', minWidth: '200px' }}
          >
            <option value="">Select a device</option>
            {devices.map(device => (
              <option key={device.client_id} value={device.client_id}>
                {device.name} ({device.device_type})
              </option>
            ))}
          </select>
        </div>
        
        <div>
          <label style={{ marginRight: '10px' }}>
            Refresh interval:
            <select 
              value={refreshInterval}
              onChange={(e) => setRefreshInterval(parseInt(e.target.value))}
              className="form-control"
              style={{ marginLeft: '10px', padding: '8px' }}
            >
              <option value="1">1 second</option>
              <option value="5">5 seconds</option>
              <option value="10">10 seconds</option>
              <option value="30">30 seconds</option>
            </select>
          </label>
          
          <button
            className="btn"
            onClick={() => setIsRefreshing(!isRefreshing)}
            style={{ marginLeft: '10px' }}
          >
            {isRefreshing ? 'Pause' : 'Resume'} Updates
          </button>
        </div>
      </div>

      {selectedDevice ? (
        <>
          {renderDeviceStatus()}
          {renderDeviceMetrics()}
          {renderSecurityAlerts()}
        </>
      ) : (
        <div className="card">
          <h2 className="card-title">No Device Selected</h2>
          <p>Please select an IoT device from the dropdown to view its metrics and security status.</p>
          
          {devices.length === 0 && (
            <div style={{ marginTop: '20px' }}>
              <p>No IoT devices found in your account.</p>
              <p>To add a device, go to the Devices page and register a new device with type 'mouse', 'keyboard', or 'headset'.</p>
            </div>
          )}
        </div>
      )}

      <div className="card">
        <h2 className="card-title">Security Recommendations</h2>
        <ul>
          <li>Monitor for unusual spikes in network traffic</li>
          <li>Use firewalls to protect your IoT devices</li>
          // dashboard/src/pages/IoTDevices.js (continuing from previous code)
          <li>Keep all device firmware up to date</li>
          <li>Use unique passwords for each device</li>
          <li>Isolate IoT devices on a separate network when possible</li>
          <li>Review security logs regularly for unusual patterns</li>
        </ul>
        
        <div style={{ marginTop: '20px', padding: '15px', backgroundColor: 'rgba(98, 0, 234, 0.1)', borderRadius: '8px' }}>
          <h3 style={{ margin: '0 0 10px 0' }}>DDoS Attack Protection</h3>
          <p style={{ margin: '0 0 10px 0' }}>
            This monitoring system detects ping flood attacks and other DDoS attempts on your gaming equipment.
            When an attack is detected, the system will:
          </p>
          <ol>
            <li>Alert you in real-time</li>
            <li>Log the attack details</li>
            <li>Provide mitigation recommendations</li>
            <li>Monitor for attack resolution</li>
          </ol>
        </div>
      </div>

      <div className="card">
        <h2 className="card-title">Attack Simulation</h2>
        <p>To test the security monitoring features, you can simulate an attack using your Kali machine:</p>
        
        <div style={{ 
          backgroundColor: 'var(--card-bg)', 
          border: '1px solid var(--border-color)',
          borderRadius: '5px',
          padding: '15px',
          fontFamily: 'monospace',
          overflow: 'auto'
        }}>
          <p style={{ margin: '0 0 10px 0', fontWeight: 'bold' }}>Ping flood attack from Kali:</p>
          <code>sudo hping3 -1 --flood -a [SPOOFED_IP] [DEVICE_IP]</code>
          <p style={{ margin: '10px 0 10px 0', fontWeight: 'bold' }}>Or using ping:</p>
          <code>ping -f -s 65500 [DEVICE_IP]</code>
          <p style={{ margin: '10px 0 0 0', fontWeight: 'bold' }}>For a more distributed attack simulation:</p>
          <code>sudo mdk3 [INTERFACE] d -c [CHANNEL] -s 1000</code>
        </div>
        
        <p style={{ marginTop: '15px', fontSize: '0.9rem', color: 'var(--error-color)' }}>
          <strong>Warning:</strong> Only perform these tests in your controlled lab environment against 
          your own devices. Unauthorized DoS attacks are illegal.
        </p>
      </div>
    </div>
  );
};

export default IoTDevices;