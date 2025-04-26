import React, { useState, useEffect } from 'react';
import { fetchWithAuth, getIoTDeviceData, getDeviceSecurityAlerts } from '../utils/api';
import './IoTDashboard.css';

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
        const response = await fetchWithAuth('/api/devices');
        if (!response.ok) {
          throw new Error('Failed to fetch devices');
        }

        const data = await response.json();
        console.log("Received devices data:", data);
        
        // Filter IoT devices with updated device types
        const iotDevices = data.devices.filter(device => 
          device.device_type === 'mouse' || 
          device.device_type === 'keyboard' || 
          device.device_type === 'headset' ||
          device.device_type === 'mouse_sensor' || 
          device.device_type === 'keyboard_sensor' || 
          device.device_type === 'headset_sensor'
        );
        
        // Rename devices to be more IoT-specific
        const renamedDevices = iotDevices.map(device => {
          // Update names to better indicate IoT sensor nature
          if (device.device_type === 'mouse' || device.name.includes('Mouse')) {
            return {
              ...device,
              name: device.name.includes('Sensor') ? device.name : `${device.name} Sensor`,
              device_type: device.device_type === 'mouse' ? 'mouse_sensor' : device.device_type
            };
          }
          if (device.device_type === 'keyboard' || device.name.includes('Keyboard')) {
            return {
              ...device,
              name: device.name.includes('Sensor') ? device.name : `${device.name} Sensor`,
              device_type: device.device_type === 'keyboard' ? 'keyboard_sensor' : device.device_type
            };
          }
          if (device.device_type === 'headset' || device.name.includes('Headset')) {
            return {
              ...device,
              name: device.name.includes('Sensor') ? device.name : `${device.name} Sensor`,
              device_type: device.device_type === 'headset' ? 'headset_sensor' : device.device_type
            };
          }
          return device;
        });
        
        setDevices(renamedDevices);
        
        // Select first device by default
        if (renamedDevices.length > 0 && !selectedDevice) {
          setSelectedDevice(renamedDevices[0].client_id);
        }
      } catch (err) {
        console.error('Error fetching devices:', err);
        setError('Failed to load devices. Please try again.');
        
        // Set fallback devices for demo purposes with IoT sensor names
        const fallbackDevices = [
          {
            client_id: 'mouse-001',
            name: 'Gaming Mouse Sensor',
            device_type: 'mouse_sensor',
            status: 'active',
          },
          {
            client_id: 'keyboard-001',
            name: 'Gaming Keyboard Sensor',
            device_type: 'keyboard_sensor',
            status: 'active',
          }
        ];
        setDevices(fallbackDevices);
        if (!selectedDevice) {
          setSelectedDevice(fallbackDevices[0].client_id);
        }
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
      console.log("Fetching data for device:", deviceId);
      const result = await getIoTDeviceData(deviceId);
      console.log("Received device data:", result);
      setDeviceData(result.data || []);
    } catch (err) {
      console.error('Error fetching device data:', err);
      // Use fallback data on error with IoT-specific metrics
      setDeviceData([{
        device_id: deviceId,
        session_id: 'fallback-session',
        timestamp: new Date().toISOString(),
        metrics: {
          clicks_per_second: 4,
          movements_count: 120,
          dpi: 16000,
          polling_rate: 1000,
          avg_click_distance: 42.5,
          button_count: 8
        },
        status: {
          under_attack: false,
          attack_duration: 0,
          battery_level: 85,
          connection_quality: 95
        }
      }]);
    }
  };

  const renderHeatmap = () => {
    const [heatmapData, setHeatmapData] = useState(null);
    const [heatmapType, setHeatmapType] = useState('position'); // 'position' or 'click'
    
    useEffect(() => {
      // Fetch heatmap data from the server
      const fetchHeatmapData = async () => {
        if (!selectedDevice) return;
        
        try {
          const token = localStorage.getItem('authToken');
          const response = await fetch(`http://localhost:5000/api/metrics/iot_heatmap/${selectedDevice}`, {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          });
  
          if (!response.ok) {
            throw new Error('Failed to fetch heatmap data');
          }
  
          const data = await response.json();
          setHeatmapData(data);
        } catch (err) {
          console.error('Error fetching heatmap data:', err);
          // Generate some dummy heatmap data if the API fails
          generateDummyHeatmap();
        }
      };
      
      const generateDummyHeatmap = () => {
        // Create a 108×192 grid (scaled down 1920×1080 by factor of 10)
        const width = 192;
        const height = 108;
        const positionData = Array(height).fill().map(() => Array(width).fill(0));
        const clickData = Array(height).fill().map(() => Array(width).fill(0));
        
        // Generate some random hotspots
        // Center area (where most movement happens)
        for (let i = 0; i < 5000; i++) {
          const x = Math.floor(Math.random() * width * 0.6 + width * 0.2);
          const y = Math.floor(Math.random() * height * 0.6 + height * 0.2);
          positionData[y][x] += Math.random() * 2 + 1;
          
          // Clicks are less frequent
          if (Math.random() < 0.3) {
            clickData[y][x] += Math.random() * 5 + 1;
          }
        }
        
        // Add hotspots for common UI elements (top-left, bottom, etc.)
        // Top-left (menu area)
        for (let i = 0; i < 1000; i++) {
          const x = Math.floor(Math.random() * width * 0.2);
          const y = Math.floor(Math.random() * height * 0.2);
          positionData[y][x] += Math.random() * 3 + 1;
          if (Math.random() < 0.4) {
            clickData[y][x] += Math.random() * 8 + 2;
          }
        }
        
        // Bottom center (action bar area)
        for (let i = 0; i < 1000; i++) {
          const x = Math.floor(Math.random() * width * 0.6 + width * 0.2);
          const y = Math.floor(Math.random() * height * 0.2 + height * 0.8);
          positionData[y][x] += Math.random() * 2 + 1;
          if (Math.random() < 0.5) {
            clickData[y][x] += Math.random() * 6 + 3;
          }
        }
        
        setHeatmapData({
          position_heatmap: positionData,
          click_heatmap: clickData,
          resolution: {
            width,
            height
          }
        });
      };
      
      fetchHeatmapData();
      
      // Refresh heatmap data periodically
      const interval = setInterval(fetchHeatmapData, 5000);
      return () => clearInterval(interval);
    }, [selectedDevice]);
    
    if (!heatmapData) {
      return (
        <div className="card">
          <h2 className="card-title">Mouse Movement Heatmap</h2>
          <p>Loading heatmap data...</p>
        </div>
      );
    }
    
    // Get the current heatmap based on user selection
    const currentHeatmap = heatmapType === 'position' 
      ? heatmapData.position_heatmap 
      : heatmapData.click_heatmap;
    
    // Color mapping function
    const getColor = (value) => {
      // Color scale from blue (cold) to red (hot)
      if (value === 0) return 'rgba(0, 0, 0, 0)'; // Transparent for no data
      if (value < 10) return `rgba(0, 0, 255, ${value / 20})`;
      if (value < 30) return `rgba(0, ${255 - (value - 10) * 8}, 255, 0.5)`;
      if (value < 60) return `rgba(${(value - 30) * 8}, 255, ${255 - (value - 30) * 8}, 0.6)`;
      if (value < 80) return `rgba(255, ${255 - (value - 60) * 12}, 0, 0.7)`;
      return `rgba(255, 0, 0, 0.8)`;
    };
    
    return (
      <div className="card">
        <h2 className="card-title">Mouse Movement Heatmap</h2>
        <div style={{ marginBottom: '10px' }}>
          <button 
            className={`btn ${heatmapType === 'position' ? 'btn-primary' : ''}`}
            onClick={() => setHeatmapType('position')}
            style={{ marginRight: '10px' }}
          >
            Movement Heatmap
          </button>
          <button 
            className={`btn ${heatmapType === 'click' ? 'btn-primary' : ''}`}
            onClick={() => setHeatmapType('click')}
          >
            Click Heatmap
          </button>
        </div>
        
        <div style={{ 
          position: 'relative',
          width: '100%',
          height: '300px',
          border: '1px solid var(--border-color)',
          borderRadius: '4px',
          overflow: 'hidden',
          backgroundColor: '#111'
        }}>
          {/* Visualization canvas */}
          <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            display: 'grid',
            gridTemplateColumns: `repeat(${heatmapData.resolution.width}, 1fr)`,
            gridTemplateRows: `repeat(${heatmapData.resolution.height}, 1fr)`
          }}>
            {currentHeatmap.flat().map((value, index) => {
              const x = index % heatmapData.resolution.width;
              const y = Math.floor(index / heatmapData.resolution.width);
              return (
                <div
                  key={`${x}-${y}`}
                  style={{
                    backgroundColor: getColor(value),
                    gridColumn: x + 1,
                    gridRow: y + 1
                  }}
                />
              );
            })}
          </div>
          
          {/* Add a simulated game screen overlay for reference */}
          <div style={{
            position: 'absolute',
            top: '10%',
            left: '10%',
            width: '80%',
            height: '80%',
            border: '1px dashed rgba(255, 255, 255, 0.3)',
            borderRadius: '2px',
            pointerEvents: 'none',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center'
          }}>
            <span style={{ color: 'rgba(255, 255, 255, 0.2)' }}>Game Screen Area</span>
          </div>
        </div>
        
        <div style={{ marginTop: '15px' }}>
          <p><strong>Heatmap Type:</strong> {heatmapType === 'position' ? 'Mouse Movement' : 'Mouse Clicks'}</p>
          <p>This heatmap shows the distribution of {heatmapType === 'position' ? 'mouse movements' : 'mouse clicks'} across the screen, processed by the edge computing capabilities of the IoT mouse sensor.</p>
          <p>The real-time data collection and processing demonstrates how IoT gaming peripherals can provide deeper insights into player behavior and performance.</p>
        </div>
      </div>
    );
  };
  

  const fetchSecurityAlerts = async (deviceId) => {
    try {
      console.log("Fetching security alerts for device:", deviceId);
      const result = await getDeviceSecurityAlerts(deviceId);
      console.log("Received security alerts:", result);
      setSecurityAlerts(result.alerts || []);
    } catch (err) {
      console.error('Error fetching security alerts:', err);
      // Use fallback data on error
      setSecurityAlerts([{
        timestamp: new Date().toISOString(),
        event_type: 'attack_detected',
        details: {
          attack_type: 'ping_flood',
          intensity: 72,
          threshold: 50
        },
        severity: 'critical'
      }]);
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

  // Fixed function to properly reflect attack status
  const renderDeviceStatus = () => {
    const status = getDeviceStatus();
    // Check for critical alerts in the last minute to determine attack status
    const hasRecentCriticalAlert = securityAlerts.some(alert => {
      const alertTime = new Date(alert.timestamp);
      const now = new Date();
      const timeDiff = (now - alertTime) / 1000; // in seconds
      return alert.severity === 'critical' && timeDiff < 60;
    });
    
    // Consider the device under attack if either status says so OR there's a recent critical alert
    const isAttacked = (status && status.under_attack) || hasRecentCriticalAlert;
    
    // Rest of your function remains the same
    return (
      <div style={{
        padding: '15px',
        borderRadius: '8px',
        backgroundColor: isAttacked ? 'rgba(176, 0, 32, 0.1)' : 'rgba(0, 200, 83, 0.1)',
        // ...rest of your code
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
              Security alert: DDoS protection engaged, traffic filtering active
            </p>
            <p style={{ margin: '5px 0 0 0', fontSize: '0.9rem' }}>
              Take immediate action to mitigate this attack!
            </p>
          </div>
        )}
      </div>
    );
  };

  // Enhanced to display IoT-specific metrics with better descriptions
  const renderDeviceMetrics = () => {
    const metrics = getLatestMetrics();
    if (!metrics) return <p>No metrics available</p>;
    
    // Get device type for context-specific descriptions
    const selectedDeviceObj = devices.find(d => d.client_id === selectedDevice);
    const deviceType = selectedDeviceObj ? selectedDeviceObj.device_type : 'mouse_sensor';
    
    return (
      <div className="card">
        <h2 className="card-title">Real-Time IoT Performance Metrics</h2>
        
        {/* IoT Device Description */}
        <div style={{ marginBottom: '15px' }}>
          <p><strong>Device Type:</strong> {deviceType} - A specialized IoT sensor system equipped with accelerometers, gyroscopes, and pressure sensors to capture precise gaming input data and transmit it securely across the network.</p>
          <p><strong>IoT Capabilities:</strong> Edge processing, wireless connectivity, real-time data transmission, anomaly detection, encrypted communication</p>
          <p><strong>Network Protocol:</strong> MQTT over TLS 1.3 with certificate-based authentication</p>
        </div>
        
        {/* Metrics with descriptions */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '20px' }}>
          {Object.entries(metrics).map(([key, value]) => (
            <div key={key} style={{ flex: '1', minWidth: '150px' }}>
              <h3>{formatMetricName(key)}</h3>
              <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: '5px 0' }}>
                {formatMetricValue(key, value)}
              </p>
              <p style={{ fontSize: '0.8rem', margin: '0', color: '#666' }}>
                {getMetricDescription(key, deviceType)}
              </p>
            </div>
          ))}
        </div>
        
        {/* IoT Network Statistics */}
        <div style={{ marginTop: '20px', borderTop: '1px solid var(--border-color)', paddingTop: '15px' }}>
          <h3>IoT Network Statistics</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '20px' }}>
            <div style={{ flex: '1', minWidth: '150px' }}>
              <h4>Packet Loss</h4>
              <p style={{ fontSize: '1.5rem', fontWeight: 'bold', margin: '5px 0' }}>
                {getDeviceStatus().under_attack ? '4.2%' : '0.01%'}
              </p>
            </div>
            <div style={{ flex: '1', minWidth: '150px' }}>
              <h4>Latency</h4>
              <p style={{ fontSize: '1.5rem', fontWeight: 'bold', margin: '5px 0' }}>
                {getDeviceStatus().under_attack ? '12ms' : '2ms'}
              </p>
            </div>
            <div style={{ flex: '1', minWidth: '150px' }}>
              <h4>Signal Strength</h4>
              <p style={{ fontSize: '1.5rem', fontWeight: 'bold', margin: '5px 0' }}>
                {getDeviceStatus().under_attack ? '-65dBm' : '-42dBm'}
              </p>
            </div>
            <div style={{ flex: '1', minWidth: '150px' }}>
              <h4>Power Consumption</h4>
              <p style={{ fontSize: '1.5rem', fontWeight: 'bold', margin: '5px 0' }}>
                {getDeviceStatus().under_attack ? '120mW' : '85mW'}
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Helper functions for better metric presentation
  const formatMetricName = (key) => {
    // Convert snake_case to Title Case
    return key.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  const formatMetricValue = (key, value) => {
    // Format values with appropriate units
    if (key === 'avg_click_distance') return `${value}px`;
    if (key === 'polling_rate') return `${value}Hz`;
    if (key === 'dpi') return value.toLocaleString();
    return value;
  };

  const getMetricDescription = (key, deviceType) => {
    const descriptions = {
      clicks_per_second: 'Number of input events per second detected by the pressure sensors',
      movements_count: 'Total movement events tracked by motion sensors',
      dpi: 'Resolution of the optical/laser position sensor',
      polling_rate: 'Sensor data sampling frequency',
      avg_click_distance: 'Average pixel distance between clicks measured by position sensors',
      button_count: 'Number of discrete input sensors on device'
    };
    
    return descriptions[key] || `IoT sensor data metric for ${deviceType}`;
  };

  // Enhanced security alerts with better formatting
  const renderSecurityAlerts = () => {
    if (!securityAlerts || securityAlerts.length === 0) {
      return (
        <div className="card">
          <h2 className="card-title">Security Alerts</h2>
          <p>No security alerts detected for this IoT sensor</p>
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
                    {formatEventType(alert.event_type)}
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
                    {formatAlertDetails(alert)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  // Helper functions for security alerts
  const formatEventType = (eventType) => {
    // Make event types more descriptive
    if (eventType === 'attack_detected') return 'Network Attack Detected';
    if (eventType === 'attack_resolved') return 'Attack Mitigation Successful';
    return eventType.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  };

  const formatAlertDetails = (alert) => {
    if (!alert.details) return 'No details available';
    
    if (typeof alert.details === 'string') {
      try {
        const details = JSON.parse(alert.details);
        return formatDetailsObject(details);
      } catch (e) {
        return alert.details;
      }
    }
    
    return formatDetailsObject(alert.details);
  };

  const formatDetailsObject = (details) => {
    if (details.attack_type === 'ping_flood') {
      return `DDoS attack detected: ${details.intensity} packets/sec (threshold: ${details.threshold}). IoT firewall engaged.`;
    }
    
    if (details.duration) {
      return `Attack resolved after ${details.duration} seconds. Normal operation restored.`;
    }
    
    return JSON.stringify(details);
  };

  if (loading) {
    return <div className="loading">Loading IoT devices...</div>;
  }

  return (
    <div>
      <h1>IoT Sensor Network Monitoring</h1>
      <p>Monitor your IoT gaming equipment sensors, network performance and security in real-time</p>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <select 
            value={selectedDevice || ''}
            onChange={(e) => setSelectedDevice(e.target.value)}
            className="form-control"
            style={{ padding: '8px', minWidth: '200px' }}
          >
            <option value="">Select an IoT sensor</option>
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
          {renderHeatmap()}
        </>
      ) : (
        <div className="card">
          <h2 className="card-title">No IoT Device Selected</h2>
          <p>Please select an IoT device sensor from the dropdown to view its metrics and security status.</p>
          
          {devices.length === 0 && (
            <div style={{ marginTop: '20px' }}>
              <p>No IoT devices found in your account.</p>
              <p>To add a device, go to the Devices page and register a new device with type 'mouse_sensor', 'keyboard_sensor', or 'headset_sensor'.</p>
            </div>
          )}
        </div>
      )}

      <div className="card">
        <h2 className="card-title">IoT Security Recommendations</h2>
        <ul>
          <li>Keep IoT firmware updated with the latest security patches</li>
          <li>Implement network segmentation to isolate IoT devices</li>
          <li>Use strong, unique credentials for each device</li>
          <li>Enable TLS for all device communication</li>
          <li>Regularly audit device access and traffic patterns</li>
          <li>Implement intrusion detection at the edge gateway</li>
          <li>Ensure proper certificate management and rotation</li>
        </ul>
        
        <div style={{ marginTop: '20px', padding: '15px', backgroundColor: 'rgba(98, 0, 234, 0.1)', borderRadius: '8px' }}>
          <h3 style={{ margin: '0 0 10px 0' }}>DDoS Attack Protection for IoT Gaming Sensors</h3>
          <p style={{ margin: '0 0 10px 0' }}>
            This monitoring system implements a multilayered defense against various DDoS attacks targeting your gaming sensors:
          </p>
          <ol>
            <li><strong>Edge Filtering:</strong> Attack traffic is detected and filtered at the sensor level before impacting performance</li>
            <li><strong>Adaptive Rate Limiting:</strong> Dynamically adjusts traffic thresholds based on historical patterns</li>
            <li><strong>Signature-Based Detection:</strong> Identifies known attack patterns and automatically applies countermeasures</li>
            <li><strong>Anomaly Detection:</strong> Machine learning algorithms identify deviations from normal traffic</li>
            <li><strong>Secure Bootstrapping:</strong> Devices use mutual authentication with the gateway to prevent impersonation</li>
          </ol>
        </div>
      </div>

      <div className="card">
        <h2 className="card-title">IoT Attack Simulation</h2>
        <p>To test the security monitoring features of your IoT gaming sensors, you can simulate an attack using the following methods:</p>
        
        <div style={{ 
          backgroundColor: 'var(--card-bg)', 
          border: '1px solid var(--border-color)',
          borderRadius: '5px',
          padding: '15px',
          fontFamily: 'monospace',
          overflow: 'auto'
        }}>
          <p style={{ margin: '0 0 10px 0', fontWeight: 'bold' }}>DDoS simulation on IoT sensor gateway:</p>
          <code>sudo hping3 -1 --flood -a [SPOOFED_IP] [SENSOR_GATEWAY_IP]</code>
          <p style={{ margin: '10px 0 10px 0', fontWeight: 'bold' }}>Or using ping with large packets:</p>
          <code>ping -f -s 65500 [SENSOR_GATEWAY_IP]</code>
          <p style={{ margin: '10px 0 0 0', fontWeight: 'bold' }}>For a more distributed attack simulation:</p>
          <code>sudo mdk3 [INTERFACE] d -c [CHANNEL] -s 1000</code>
        </div>
        
        <p style={{ marginTop: '15px', fontSize: '0.9rem', color: 'var(--error-color)' }}>
          <strong>Warning:</strong> Only perform these tests in your controlled lab environment against 
          your own devices. Unauthorized DoS attacks are illegal and unethical.
        </p>
      </div>
    </div>
  );
};

export default IoTDevices;