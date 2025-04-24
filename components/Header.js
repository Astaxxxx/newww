import React from 'react';
import '../App.css';

const Header = ({ user, onLogout, darkMode, toggleDarkMode }) => {
  return (
    <header className="header">
      <div className="header-logo">Secure Esports Tracker</div>
      
      <div className="header-actions">
        <span style={{ marginRight: '20px' }}>
          Welcome, {user.username}
        </span>
        
        <button 
          className="btn"
          onClick={toggleDarkMode}
          style={{ 
            backgroundColor: 'transparent', 
            border: '1px solid white',
            color: 'white',
            marginRight: '10px'
          }}
        >
          {darkMode ? '☀️ Light' : '🌙 Dark'}
        </button>
        
        <button 
          className="btn"
          onClick={onLogout}
          style={{ 
            backgroundColor: 'rgba(255, 255, 255, 0.2)', 
            color: 'white',
            border: 'none'
          }}
        >
          Logout
        </button>
      </div>
    </header>
  );
};

export default Header;