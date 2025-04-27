import React, { useState, useEffect } from 'react';

const MouseButtonHeatmap = ({ deviceId }) => {
  const [heatmapData, setHeatmapData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchHeatmapData = async () => {
      if (!deviceId) return;
      
      try {
        const token = localStorage.getItem('authToken');
        const response = await fetch(`http://localhost:5000/api/metrics/mouse_contact_heatmap/${deviceId}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (!response.ok) {
          throw new Error('Failed to fetch mouse contact heatmap data');
        }

        const data = await response.json();
        setHeatmapData(data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching mouse contact data:', err);
        setError(err.message);
        // Generate fallback data for demonstration
        generateFallbackData();
      }
    };
    
    const generateFallbackData = () => {
      // Create realistic fallback data showing contact points on the mouse surface
      const fallbackData = {
        // Contact points heatmap (0-100 intensity scale)
        contact_points: {
          // Top surface (main clicks)
          'top_left': 92,       // Index finger position (left click)
          'top_right': 74,      // Middle finger position (right click)
          'top_middle': 45,     // Area between buttons
          
          // Side surfaces
          'left_front': 87,     // Thumb front position
          'left_back': 65,      // Thumb back position
          'left_bottom': 53,    // Lower thumb rest area
          'right_side': 28,     // Right side of mouse (pinky area)
          
          // Bottom contact areas
          'palm_rest': 80,      // Palm contact area
          'wrist_area': 50,     // Wrist contact point
        },
        
        // Pressure data (0-100 scale)
        pressure: {
          'top_left': 88,       // Left click pressure
          'top_right': 72,      // Right click pressure
          'left_front': 92,     // Thumb pressure (side buttons)
          'palm_rest': 65,      // Palm pressure
        },
        
        // Click count data
        click_data: {
          'left_click': 6452,   // Count of left clicks
          'right_click': 2341,  // Count of right clicks
          'middle_click': 478,  // Count of middle clicks
          'side_button_1': 965, // Count of side button 1 clicks
          'side_button_2': 1247 // Count of side button 2 clicks
        },
        
        // Finger position data
        finger_position: {
          'index_finger': {
            'x_offset': 2,      // Lateral position offset in mm (0 is centered)
            'y_offset': -3,     // Forward/backward position offset (negative is forward)
            'angle': 12         // Finger angle in degrees
          },
          'middle_finger': {
            'x_offset': -1,
            'y_offset': 4,
            'angle': 8
          },
          'thumb': {
            'x_offset': 5,
            'y_offset': 7,
            'angle': 22
          }
        },
        
        // Posture analysis
        posture_issues: [
          {
            'issue': 'excessive_wrist_extension',
            'severity': 'medium',
            'description': 'Your wrist is extended upward too much'
          },
          {
            'issue': 'thumb_overextension',
            'severity': 'high',
            'description': 'Your thumb is stretched too far to reach the side buttons'
          }
        ],
        
        timestamp: new Date().toISOString()
      };
      
      setHeatmapData(fallbackData);
      setLoading(false);
    };
    
    fetchHeatmapData();
    
    // Refresh data periodically
    const interval = setInterval(fetchHeatmapData, 10000);
    return () => clearInterval(interval);
  }, [deviceId]);
  
  if (loading) {
    return (
      <div className="card">
        <h2 className="card-title">Mouse Physical Contact Analysis</h2>
        <p>Loading mouse contact data...</p>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="card">
        <h2 className="card-title">Mouse Physical Contact Analysis</h2>
        <p className="error">Error: {error}</p>
      </div>
    );
  }
  
  // Helper function to get color based on intensity
  const getHeatColor = (value) => {
    // Scale from blue (low) to red (high)
    if (value < 20) return `rgba(0, 0, 255, ${value / 100})`;
    if (value < 50) return `rgba(0, ${255 - ((value - 20) * 255 / 30)}, 255, ${value / 100})`;
    if (value < 80) return `rgba(${((value - 50) * 255 / 30)}, 0, ${255 - ((value - 50) * 255 / 30)}, ${value / 100})`;
    return `rgba(255, 0, 0, ${value / 100})`;
  };
  
  // Helper function to get text color based on background intensity
  const getTextColor = (value) => {
    return value > 50 ? 'white' : 'black';
  };
  
  return (
    <div className="card">
      <h2 className="card-title">Mouse Physical Contact Analysis</h2>
      <p>IoT sensor data showing contact points and pressure on the physical mouse device</p>
      
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '20px' }}>
        {/* 3D mouse visualization with contact heatmap */}
        <div style={{ 
          position: 'relative',
          width: '400px', 
          height: '300px',
          margin: '20px auto',
          perspective: '800px'
        }}>
          {/* Top view of mouse */}
          <div style={{ 
            position: 'absolute',
            top: '50px',
            left: '100px',
            width: '200px', 
            height: '120px',
            backgroundColor: '#333',
            borderRadius: '60px 60px 120px 120px',
            boxShadow: '0 5px 15px rgba(0,0,0,0.3)',
            transform: 'rotateX(45deg)',
            transformStyle: 'preserve-3d'
          }}>
            {/* Left click area */}
            <div style={{ 
              position: 'absolute',
              top: '0',
              left: '0',
              width: '100px',
              height: '60px',
              borderRadius: '60px 0 0 0',
              backgroundColor: getHeatColor(heatmapData.contact_points.top_left),
              border: '1px solid #222',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              color: getTextColor(heatmapData.contact_points.top_left),
              fontSize: '10px'
            }}>
              {heatmapData.contact_points.top_left}%
            </div>
            
            {/* Right click area */}
            <div style={{ 
              position: 'absolute',
              top: '0',
              right: '0',
              width: '100px',
              height: '60px',
              borderRadius: '0 60px 0 0',
              backgroundColor: getHeatColor(heatmapData.contact_points.top_right),
              border: '1px solid #222',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              color: getTextColor(heatmapData.contact_points.top_right),
              fontSize: '10px'
            }}>
              {heatmapData.contact_points.top_right}%
            </div>
            
            {/* Scroll wheel area */}
            <div style={{ 
              position: 'absolute',
              top: '15px',
              left: '90px',
              width: '20px',
              height: '30px',
              borderRadius: '5px',
              backgroundColor: getHeatColor(heatmapData.contact_points.top_middle),
              border: '1px solid #222'
            }}></div>
            
            {/* Palm rest area */}
            <div style={{ 
              position: 'absolute',
              bottom: '0',
              left: '40px',
              width: '120px',
              height: '50px',
              borderRadius: '0 0 120px 120px',
              backgroundColor: getHeatColor(heatmapData.contact_points.palm_rest),
              border: '1px solid #222',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              color: getTextColor(heatmapData.contact_points.palm_rest),
              fontSize: '10px'
            }}>
              {heatmapData.contact_points.palm_rest}%
            </div>
          </div>
          
          {/* Side view left (thumb area) */}
          <div style={{ 
            position: 'absolute',
            top: '100px',
            left: '75px',
            width: '25px',
            height: '100px',
            backgroundColor: '#444',
            borderRadius: '10px 0 0 20px',
            transform: 'rotateY(-60deg)',
            transformStyle: 'preserve-3d'
          }}>
            {/* Thumb front position (for side buttons) */}
            <div style={{ 
              position: 'absolute',
              top: '30px',
              left: '0',
              width: '25px',
              height: '30px',
              backgroundColor: getHeatColor(heatmapData.contact_points.left_front),
              borderRadius: '10px 0 0 0',
              border: '1px solid #222',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              color: getTextColor(heatmapData.contact_points.left_front),
              fontSize: '10px',
              transform: 'rotateY(60deg)'
            }}>
              {heatmapData.contact_points.left_front}%
            </div>
            
            {/* Thumb back position */}
            <div style={{ 
              position: 'absolute',
              top: '60px',
              left: '0',
              width: '25px',
              height: '40px',
              backgroundColor: getHeatColor(heatmapData.contact_points.left_back),
              borderRadius: '0 0 0 20px',
              border: '1px solid #222',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              color: getTextColor(heatmapData.contact_points.left_back),
              fontSize: '10px',
              transform: 'rotateY(60deg)'
            }}>
              {heatmapData.contact_points.left_back}%
            </div>
          </div>
          
          {/* Side view right (pinky area) */}
          <div style={{ 
            position: 'absolute',
            top: '100px',
            right: '75px',
            width: '25px',
            height: '100px',
            backgroundColor: '#444',
            borderRadius: '0 10px 20px 0',
            transform: 'rotateY(60deg)',
            transformStyle: 'preserve-3d'
          }}>
            <div style={{ 
              position: 'absolute',
              top: '30px',
              right: '0',
              width: '25px',
              height: '70px',
              backgroundColor: getHeatColor(heatmapData.contact_points.right_side),
              borderRadius: '0 10px 20px 0',
              border: '1px solid #222',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              color: getTextColor(heatmapData.contact_points.right_side),
              fontSize: '10px',
              transform: 'rotateY(-60deg)'
            }}>
              {heatmapData.contact_points.right_side}%
            </div>
          </div>
        </div>
        
        {/* Click Statistics */}
        <div style={{ width: '100%', marginTop: '20px' }}>
          <h3>Button Usage Statistics</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '15px' }}>
            {Object.entries(heatmapData.click_data).map(([buttonName, clickCount]) => (
              <div key={buttonName} style={{ 
                flex: '1', 
                minWidth: '150px',
                padding: '15px',
                backgroundColor: 'var(--card-bg)', 
                borderRadius: '8px',
                border: '1px solid var(--border-color)'
              }}>
                <h4 style={{ margin: '0 0 10px 0' }}>{buttonName.replace(/_/g, ' ').toUpperCase()}</h4>
                <div style={{ 
                  fontSize: '24px', 
                  fontWeight: 'bold',
                  textAlign: 'center',
                  margin: '10px 0'
                }}>
                  {clickCount.toLocaleString()}
                </div>
                <div style={{ 
                  fontSize: '12px',
                  textAlign: 'center',
                  color: '#666'
                }}>
                  total clicks
                </div>
              </div>
            ))}
          </div>
        </div>
        
        {/* Posture Issues and Recommendations */}
        <div style={{ 
          width: '100%',
          marginTop: '20px',
          padding: '15px',
          backgroundColor: 'rgba(98, 0, 234, 0.1)',
          borderRadius: '8px',
          border: '1px solid var(--primary-color)'
        }}>
          <h3 style={{ margin: '0 0 10px 0' }}>Ergonomic Analysis & Recommendations</h3>
          
          {heatmapData.posture_issues.length > 0 ? (
            <ul style={{ margin: '0', paddingLeft: '20px' }}>
              {heatmapData.posture_issues.map((issue, index) => (
                <li key={index} style={{ marginBottom: '10px' }}>
                  <strong style={{ 
                    color: issue.severity === 'high' ? 'var(--error-color)' : 
                           issue.severity === 'medium' ? '#ff9800' : 'var(--success-color)'
                  }}>
                    {issue.issue.replace(/_/g, ' ').toUpperCase()} ({issue.severity}):
                  </strong> {issue.description}
                </li>
              ))}
            </ul>
          ) : (
            <p>No significant posture issues detected. Your hand position looks good!</p>
          )}
          
          {/* General recommendations */}
          <h4 style={{ marginTop: '15px' }}>General Recommendations:</h4>
          <ul style={{ margin: '0', paddingLeft: '20px' }}>
            <li>Keep your wrist in a neutral position, not bent upward or downward</li>
            <li>Adjust mouse sensitivity to reduce excessive movement</li>
            <li>Position the mouse close enough to avoid stretching</li>
            <li>Use a mouse size appropriate for your hand dimensions</li>
            <li>Consider a vertical or ergonomic mouse design if discomfort persists</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default MouseButtonHeatmap;