import React from 'react';

const AttackAlert = ({ attack }) => {
  const severity = attack.packet_count > 1000 ? 'CRITICAL' : 'WARNING';

  return (
    <div className="attack-alert">
      <div className="attack-header">
        <span className="timestamp">
          {new Date(attack.timestamp).toLocaleString()}
        </span>
        <span className={`severity ${severity.toLowerCase()}`}>
          {severity}
        </span>
      </div>
      <div className="attack-details">
        <p>Attack detected on {attack.device_type}</p>
        <p>Source: {attack.attack_source}</p>
        <p>Packets: {attack.packet_count}</p>
      </div>
    </div>
  );
};

export default AttackAlert;
