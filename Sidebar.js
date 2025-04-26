import React from 'react';
import { NavLink } from 'react-router-dom';
import '../App.css';

const Sidebar = ({ user }) => {
  return (
    <div className="sidebar">
      <ul className="sidebar-nav">
        <li className="nav-item">
          <NavLink to="/" className="nav-link" end>
            <span className="nav-icon">📊</span>
            <span className="nav-text">Dashboard</span>
          </NavLink>
        </li>
        
        <li className="nav-item">
          <NavLink to="/devices" className="nav-link">
            <span className="nav-icon">⌨️</span>
            <span className="nav-text">Devices</span>
          </NavLink>
        </li>
        
        <li className="nav-item">
          <NavLink to="/iot" className="nav-link">
            <span className="nav-icon">🔌</span>
            <span className="nav-text">IoT Devices</span>
          </NavLink>
        </li>
        
        <li className="nav-item">
          <NavLink to="/sessions" className="nav-link">
            <span className="nav-icon">🎮</span>
            <span className="nav-text">Sessions</span>
          </NavLink>
        </li>
        
        {user && user.role === 'admin' && (
          <li className="nav-item">
            <NavLink to="/security" className="nav-link">
              <span className="nav-icon">🔒</span>
              <span className="nav-text">Security Logs</span>
            </NavLink>
          </li>
        )}
        
        <li className="nav-item">
          <NavLink to="/settings" className="nav-link">
            <span className="nav-icon">⚙️</span>
            <span className="nav-text">Settings</span>
          </NavLink>
        </li>
      </ul>
      
      <div style={{ padding: '20px', marginTop: '20px', borderTop: '1px solid var(--border-color)' }}>
        <h4 style={{ marginTop: 0 }}>Performance Summary</h4>
        <div>
          <p><strong>Avg. APM:</strong> 134</p>
          <p><strong>Last Session:</strong> 2 hours ago</p>
          <p><strong>Active Devices:</strong> 1</p>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;