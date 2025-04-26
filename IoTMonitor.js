import React, { useState, useEffect } from 'react';
import { getDevices } from '../utils/api';
import '../App.css';

const IoTMonitor = ({ user }) => {
    const [devices, setDevices] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 1000);
        return () => clearInterval(interval);
    }, []);

    const fetchData = async () => {
        try {
            const response = await getDevices();
            setDevices(response.devices || []);
            setError(null);
        } catch (err) {
            setError('Failed to fetch device data');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div className="loading">Loading IoT devices...</div>;

    return (
        <div className="iot-monitor">
            <h1>IoT Device Monitor</h1>
            <div className="device-grid">
                {devices.map(device => (
                    <div key={device.client_id} className="device-card">
                        <h3>{device.name}</h3>
                        <p>Type: {device.device_type}</p>
                        <p>Status: {device.status}</p>
                        {device.metrics && (
                            <div className="metrics">
                                <p>Connection Quality: {device.metrics.connection_quality}%</p>
                                <p>Input Rate: {device.metrics.input_rate}</p>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default IoTMonitor;
