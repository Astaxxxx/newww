import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import './App.css';

// Component imports
import Login from './components/Login';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import DeviceManager from './pages/DeviceManager';
import SessionHistory from './pages/SessionHistory';
import SecurityLogs from './pages/SecurityLogs';
import Settings from './pages/Settings';
import IoTDevices from './pages/IoTDevices';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [darkMode, setDarkMode] = useState(localStorage.getItem('darkMode') === 'true');

  // Check authentication on load
// In your App.js or auth handling code
useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('authToken');
        if (!token) {
          setIsAuthenticated(false);
          setLoading(false);
          return;
        }
  
        // Add this code to handle expired tokens
        try {
          const response = await fetch('http://localhost:5000/api/auth/verify', {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
  
          if (response.status === 401) {
            // Token expired, clear it and redirect to login
            localStorage.removeItem('authToken');
            setIsAuthenticated(false);
            setLoading(false);
            return;
          }
  
          // Token is valid
          const userData = await response.json();
          setUser(userData);
          setIsAuthenticated(true);
        } catch (error) {
          // Handle network errors
          console.error("Token verification failed:", error);
          // Optional: Still use the token if server is unreachable
        }
      } finally {
        setLoading(false);
      }
    };
  
    checkAuth();
  }, []);

  const handleLogin = (userData, token) => {
    localStorage.setItem('authToken', token);
    setUser(userData);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    setUser(null);
    setIsAuthenticated(false);
  };

  const toggleDarkMode = () => {
    const newMode = !darkMode;
    setDarkMode(newMode);
    localStorage.setItem('darkMode', newMode.toString());
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <Router>
      <div className={`app ${darkMode ? 'dark-mode' : ''}`}>
        {isAuthenticated ? (
          <>
            <Header user={user} onLogout={handleLogout} darkMode={darkMode} toggleDarkMode={toggleDarkMode} />
            <div className="main-container">
              <Sidebar user={user} />
              <main className="content">
              <Routes>
                <Route path="/" element={<Dashboard user={user} />} />
                <Route path="/devices" element={<DeviceManager user={user} />} />
                <Route path="/sessions" element={<SessionHistory user={user} />} />
                <Route path="/security" element={<SecurityLogs user={user} />} />
                <Route path="/iot" element={<IoTDevices user={user} />} />
                <Route path="/settings" element={<Settings user={user} />} />
                <Route path="*" element={<Navigate to="/" />} />
              </Routes>
              </main>
            </div>
          </>
        ) : (
          <Login onLogin={handleLogin} />
        )}
      </div>
    </Router>
  );
}

export default App;