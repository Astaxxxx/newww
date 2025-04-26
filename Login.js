import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import '../App.css';
import { login } from '../utils/api';

const Login = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const location = useLocation();

  useEffect(() => {
    // Check if redirected due to expired session
    const queryParams = new URLSearchParams(location.search);
    const sessionExpired = queryParams.get('session') === 'expired';
    
    if (sessionExpired) {
      setError('Your session has expired. Please log in again.');
    }
  }, [location]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!username || !password) {
      setError('Please enter both username and password');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const data = await login(username, password);
      onLogin(data.user, data.token);
    } catch (err) {
      setError(err.message || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1>Secure Esports Equipment Tracker</h1>
          <h2>Login</h2>
        </div>
        
        {error && <div className="error-message">{error}</div>}
        
        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              className="form-control"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
              autoComplete="username"
              disabled={loading}
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              className="form-control"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              autoComplete="current-password"
              disabled={loading}
            />
          </div>
          
          <button 
            type="submit" 
            className="login-button"
            disabled={loading}
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
        
        <div className="login-footer" style={{ marginTop: '20px', textAlign: 'center' }}>
          <p>Track your gaming equipment performance securely</p>
          <p className="security-note" style={{ fontSize: '0.8rem', color: '#666' }}>
            All data is end-to-end encrypted
          </p>
          <div style={{ marginTop: '20px', fontSize: '0.8rem' }}>
            <p>For demo, use:</p>
            <p>Username: admin, Password: admin</p>
            <p>Username: user, Password: user</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;