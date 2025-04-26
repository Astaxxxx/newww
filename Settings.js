import React, { useState } from 'react';
import '../App.css';

const Settings = ({ user }) => {
  const [privacySettings, setPrivacySettings] = useState({
    collectKeystrokes: false,
    collectMouseMovements: true,
    sharePerformanceData: false,
    retentionPeriod: '30',
    anonymizeData: true
  });

  const [securitySettings, setSecuritySettings] = useState({
    encryptionEnabled: true,
    autoLogout: '60',
    notifyOnLogin: true,
    twoFactorAuth: false
  });

  const [interfaceSettings, setInterfaceSettings] = useState({
    showApmCounter: true,
    notificationsEnabled: true,
    sessionReminders: false,
    dataUpdateInterval: '10'
  });

  const [saveStatus, setSaveStatus] = useState('');

  const handlePrivacyChange = (e) => {
    const { name, value, type, checked } = e.target;
    setPrivacySettings({
      ...privacySettings,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleSecurityChange = (e) => {
    const { name, value, type, checked } = e.target;
    setSecuritySettings({
      ...securitySettings,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleInterfaceChange = (e) => {
    const { name, value, type, checked } = e.target;
    setInterfaceSettings({
      ...interfaceSettings,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleSaveSettings = async () => {
    try {
      // In a real implementation, would send to server
      const token = localStorage.getItem('authToken');
      const settings = {
        privacy: privacySettings,
        security: securitySettings,
        interface: interfaceSettings
      };

      // Simulated API call
      // const response = await fetch('http://localhost:5000/api/users/settings', {
      //   method: 'PUT',
      //   headers: {
      //     'Authorization': `Bearer ${token}`,
      //     'Content-Type': 'application/json'
      //   },
      //   body: JSON.stringify(settings)
      // });

      // For demo, just simulate success
      setSaveStatus('Settings saved successfully!');
      setTimeout(() => setSaveStatus(''), 3000);
    } catch (err) {
      console.error('Error saving settings:', err);
      setSaveStatus('Failed to save settings. Please try again.');
      setTimeout(() => setSaveStatus(''), 3000);
    }
  };

  return (
    <div>
      <h1>Settings</h1>
      <p>Configure your preferences for the Secure Esports Equipment Tracker</p>

      {saveStatus && (
        <div className={`card`} style={{ 
          backgroundColor: saveStatus.includes('Failed') ? 'rgba(176, 0, 32, 0.1)' : 'rgba(0, 200, 83, 0.1)',
          color: saveStatus.includes('Failed') ? 'var(--error-color)' : 'var(--success-color)',
          marginBottom: '20px'
        }}>
          <p style={{ margin: 0 }}>{saveStatus}</p>
        </div>
      )}

      <div className="card">
        <h2 className="card-title">Privacy Settings</h2>
        <div className="form-group">
          <label className="checkbox-container">
            <input
              type="checkbox"
              name="collectKeystrokes"
              checked={privacySettings.collectKeystrokes}
              onChange={handlePrivacyChange}
            />
            <span className="checkbox-text">Collect specific keystrokes for analysis</span>
          </label>
          <p className="setting-description">
            When disabled, only keystroke counts are collected, not the specific keys
          </p>
        </div>

        <div className="form-group">
          <label className="checkbox-container">
            <input
              type="checkbox"
              name="collectMouseMovements"
              checked={privacySettings.collectMouseMovements}
              onChange={handlePrivacyChange}
            />
            <span className="checkbox-text">Collect mouse movement data</span>
          </label>
          <p className="setting-description">
            Track mouse movements for detailed performance analysis
          </p>
        </div>

        <div className="form-group">
          <label className="checkbox-container">
            <input
              type="checkbox"
              name="sharePerformanceData"
              checked={privacySettings.sharePerformanceData}
              onChange={handlePrivacyChange}
            />
            <span className="checkbox-text">Share anonymized performance data</span>
          </label>
          <p className="setting-description">
            Contribute anonymous data to improve esports performance analysis
          </p>
        </div>

        <div className="form-group">
          <label htmlFor="retentionPeriod">Data retention period (days)</label>
          <select
            id="retentionPeriod"
            name="retentionPeriod"
            className="form-control"
            value={privacySettings.retentionPeriod}
            onChange={handlePrivacyChange}
          >
            <option value="7">7 days</option>
            <option value="30">30 days</option>
            <option value="90">90 days</option>
            <option value="180">180 days</option>
            <option value="365">1 year</option>
          </select>
          <p className="setting-description">
            Data older than this will be automatically deleted
          </p>
        </div>

        <div className="form-group">
          <label className="checkbox-container">
            <input
              type="checkbox"
              name="anonymizeData"
              checked={privacySettings.anonymizeData}
              onChange={handlePrivacyChange}
            />
            <span className="checkbox-text">Anonymize personal identifiers</span>
          </label>
          <p className="setting-description">
            Remove personal identifiers from stored data
          </p>
        </div>
      </div>

      <div className="card">
        <h2 className="card-title">Security Settings</h2>
        <div className="form-group">
          <label className="checkbox-container">
            <input
              type="checkbox"
              name="encryptionEnabled"
              checked={securitySettings.encryptionEnabled}
              onChange={handleSecurityChange}
            />
            <span className="checkbox-text">Enable end-to-end encryption</span>
          </label>
          <p className="setting-description">
            Encrypt all data before sending to server (recommended)
          </p>
        </div>

        <div className="form-group">
          <label htmlFor="autoLogout">Auto logout after inactivity (minutes)</label>
          <select
            id="autoLogout"
            name="autoLogout"
            className="form-control"
            value={securitySettings.autoLogout}
            onChange={handleSecurityChange}
          >
            <option value="15">15 minutes</option>
            <option value="30">30 minutes</option>
            <option value="60">1 hour</option>
            <option value="120">2 hours</option>
            <option value="never">Never</option>
          </select>
        </div>

        <div className="form-group">
          <label className="checkbox-container">
            <input
              type="checkbox"
              name="notifyOnLogin"
              checked={securitySettings.notifyOnLogin}
              onChange={handleSecurityChange}
            />
            <span className="checkbox-text">Notify on new login</span>
          </label>
          <p className="setting-description">
            Receive notifications when your account is accessed
          </p>
        </div>

        <div className="form-group">
          <label className="checkbox-container">
            <input
              type="checkbox"
              name="twoFactorAuth"
              checked={securitySettings.twoFactorAuth}
              onChange={handleSecurityChange}
            />
            <span className="checkbox-text">Enable two-factor authentication</span>
          </label>
          <p className="setting-description">
            Require a verification code in addition to password (coming soon)
          </p>
        </div>
      </div>

      <div className="card">
        <h2 className="card-title">Interface Settings</h2>
        <div className="form-group">
          <label className="checkbox-container">
            <input
              type="checkbox"
              name="showApmCounter"
              checked={interfaceSettings.showApmCounter}
              onChange={handleInterfaceChange}
            />
            <span className="checkbox-text">Show APM counter in real-time</span>
          </label>
          <p className="setting-description">
            Display your actions per minute while gaming
          </p>
        </div>

        <div className="form-group">
          <label className="checkbox-container">
            <input
              type="checkbox"
              name="notificationsEnabled"
              checked={interfaceSettings.notificationsEnabled}
              onChange={handleInterfaceChange}
            />
            <span className="checkbox-text">Enable desktop notifications</span>
          </label>
          <p className="setting-description">
            Show notifications for important events
          </p>
        </div>

        <div className="form-group">
          <label className="checkbox-container">
            <input
              type="checkbox"
              name="sessionReminders"
              checked={interfaceSettings.sessionReminders}
              onChange={handleInterfaceChange}
            />
            <span className="checkbox-text">Session break reminders</span>
          </label>
          <p className="setting-description">
            Get reminded to take breaks during long gaming sessions
          </p>
        </div>

        <div className="form-group">
          <label htmlFor="dataUpdateInterval">Data update interval (seconds)</label>
          <select
            id="dataUpdateInterval"
            name="dataUpdateInterval"
            className="form-control"
            value={interfaceSettings.dataUpdateInterval}
            onChange={handleInterfaceChange}
          >
            <option value="5">5 seconds</option>
            <option value="10">10 seconds</option>
            <option value="30">30 seconds</option>
            <option value="60">1 minute</option>
          </select>
          <p className="setting-description">
            How often to send performance data to the server
          </p>
        </div>
      </div>

      <div style={{ marginTop: '20px' }}>
        <button 
          className="btn btn-primary" 
          onClick={handleSaveSettings}
          style={{ marginRight: '10px' }}
        >
          Save Settings
        </button>
        <button 
          className="btn" 
          onClick={() => window.location.reload()}
        >
          Reset
        </button>
      </div>

      <div className="card" style={{ marginTop: '20px', backgroundColor: 'rgba(98, 0, 234, 0.1)' }}>
        <h2 className="card-title">Account Information</h2>
        <p><strong>Username:</strong> {user.username}</p>
        <p><strong>Role:</strong> {user.role}</p>
        <p><strong>Registered Devices:</strong> 2</p>
        <p><strong>Data Storage:</strong> 1.2 MB</p>
      </div>
    </div>
  );
};

export default Settings;