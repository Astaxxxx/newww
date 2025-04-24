import React from 'react';

const DeviceCard = ({ type, metrics }) => {
  const isUnderAttack = metrics.connection_quality < 50;

  return (
    <div className={`device-card ${isUnderAttack ? 'under-attack' : ''}`}>
      <h3>{type.toUpperCase()}</h3>
      <div className="metrics-container">
        <div className="metric">
          <label>Input Rate</label>
          <span>{metrics.input_rate}/min</span>
        </div>
        <div className="metric">
          <label>Response Time</label>
          <span>{metrics.response_time.toFixed(1)}ms</span>
        </div>
        <div className="metric">
          <label>Battery</label>
          <div className="progress-bar">
            <div 
              className="progress" 
              style={{width: `${metrics.battery_level}%`}}
            />
          </div>
          <span>{Math.round(metrics.battery_level)}%</span>
        </div>
        <div className="metric">
          <label>Connection</label>
          <div className="progress-bar">
            <div 
              className="progress"
              style={{
                width: `${metrics.connection_quality}%`,
                backgroundColor: isUnderAttack ? 'var(--error-color)' : 'var(--success-color)'
              }}
            />
          </div>
          <span>{Math.round(metrics.connection_quality)}%</span>
        </div>
      </div>
    </div>
  );
};

export default DeviceCard;
