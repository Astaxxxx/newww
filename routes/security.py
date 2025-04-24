# Add these routes to server/routes/security.py (create this file if it doesn't exist)

@app.route('/api/security/alert', methods=['POST', 'OPTIONS'])
def receive_security_alert():
    """Receive security alerts from IoT devices"""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = request.json
        device_id = data.get('device_id')
        event_type = data.get('event_type')
        details = data.get('details')
        
        if not device_id or not event_type:
            return jsonify({'error': 'Missing required fields'}), 400
            
        # Determine severity based on event type
        severity = 'critical' if event_type == 'attack_detected' else 'warning'
        
        # Log the security event
        log_security_event(
            event_type=f'iot_{event_type}', 
            details={
                'device_id': device_id,
                'details': details
            },
            severity=severity
        )
        
        # Add to device-specific alerts list
        if not hasattr(app, 'device_alerts'):
            app.device_alerts = {}
            
        if device_id not in app.device_alerts:
            app.device_alerts[device_id] = []
            
        alert_data = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'details': details,
            'severity': severity
        }
        
        app.device_alerts[device_id].append(alert_data)
        
        # Keep only the latest 100 alerts per device
        app.device_alerts[device_id] = app.device_alerts[device_id][-100:]
        
        return jsonify({'status': 'success'})
        
    except Exception as e:
        logger.error(f"Error processing security alert: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/security/device_alerts/<device_id>', methods=['GET', 'OPTIONS'])
@require_auth
def get_device_alerts(device_id):
    """Get security alerts for a specific device"""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        if not hasattr(app, 'device_alerts') or device_id not in app.device_alerts:
            return jsonify({'alerts': []})
            
        return jsonify({'alerts': app.device_alerts[device_id]})
        
    except Exception as e:
        logger.error(f"Error retrieving device alerts: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/metrics/iot_data', methods=['POST', 'OPTIONS'])
def receive_iot_data():
    """Receive IoT device data"""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = request.json
        device_id = data.get('device_id')
        
        if not device_id:
            return jsonify({'error': 'Missing device ID'}), 400
            
        # Store the data (in a real implementation, would save to database)
        if not hasattr(app, 'iot_data'):
            app.iot_data = {}
            
        if device_id not in app.iot_data:
            app.iot_data[device_id] = []
            
        app.iot_data[device_id].append(data)
        
        # Keep only the latest 100 data points per device
        app.iot_data[device_id] = app.iot_data[device_id][-100:]
        
        return jsonify({'status': 'success'})
        
    except Exception as e:
        logger.error(f"Error processing IoT data: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/metrics/iot_data/<device_id>', methods=['GET', 'OPTIONS'])
@require_auth
def get_iot_data(device_id):
    """Get IoT device data"""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        if not hasattr(app, 'iot_data') or device_id not in app.iot_data:
            return jsonify({'data': []})
            
        return jsonify({'data': app.iot_data[device_id]})
        
    except Exception as e:
        logger.error(f"Error retrieving IoT data: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500