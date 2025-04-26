from flask import request, jsonify, current_app
from datetime import datetime
import json
import logging

# Get logger
logger = logging.getLogger('server')

def register_security_routes(app):
    """Register security-related routes with the Flask app"""
    
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
            logger.info(f"SECURITY EVENT: iot_{event_type} - {json.dumps(details)}")
            
            # Add to security events list
            if hasattr(app, 'log_security_event'):
                app.log_security_event(f'iot_{event_type}', details, severity=severity)
            
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
        
    @app.route('/api/metrics/iot_heatmap/<device_id>', methods=['GET', 'OPTIONS'])
    @require_auth
    def get_iot_heatmap(device_id):
        """Get heatmap data for an IoT device"""
        # Handle OPTIONS request for CORS preflight
        if request.method == 'OPTIONS':
            return '', 204
            
        try:
            # Check if we have MQTT data for this device
            # In a real implementation, this would come from a database
            # For simulation purposes, we'll generate random data
            
            # Grid dimensions (scaled down screen resolution)
            width = 192  # 1920 / 10
            height = 108  # 1080 / 10
            
            # Create heatmap data structures
            import numpy as np
            
            # Seed with device_id to get consistent results
            import hashlib
            seed = int(hashlib.md5(device_id.encode()).hexdigest(), 16) % 10000
            np.random.seed(seed)
            
            position_heatmap = np.zeros((height, width))
            click_heatmap = np.zeros((height, width))
            
            # Generate hotspots based on typical gaming patterns
            # Center area (where most movement happens)
            center_x = width // 2
            center_y = height // 2
            
            # Add Gaussian distribution around center
            for i in range(5000):
                x = int(np.clip(np.random.normal(center_x, width/6), 0, width-1))
                y = int(np.clip(np.random.normal(center_y, height/6), 0, height-1))
                position_heatmap[y, x] += np.random.random() * 2 + 1
                
                # Clicks are less frequent
                if np.random.random() < 0.3:
                    click_heatmap[y, x] += np.random.random() * 5 + 1
            
            # Add hotspot in top-left (menu area)
            for i in range(1000):
                x = int(np.clip(np.random.normal(width/10, width/20), 0, width/5))
                y = int(np.clip(np.random.normal(height/10, height/20), 0, height/5))
                position_heatmap[y, x] += np.random.random() * 3 + 1
                if np.random.random() < 0.4:
                    click_heatmap[y, x] += np.random.random() * 8 + 2
                    
            # Add hotspot in bottom center (action bar area)
            for i in range(1000):
                x = int(np.clip(np.random.normal(center_x, width/6), center_x-width/5, center_x+width/5))
                y = int(np.clip(np.random.normal(height*0.9, height/20), height*0.8, height-1))
                position_heatmap[y, x] += np.random.random() * 2 + 1
                if np.random.random() < 0.5:
                    click_heatmap[y, x] += np.random.random() * 6 + 3
            
            # Add time variation (make it slightly different each time)
            current_time = int(time.time())
            np.random.seed(current_time % 10000)
            
            # Add some random noise
            position_heatmap += np.random.random((height, width)) * 5
            click_heatmap += np.random.random((height, width)) * 2
            
            # Normalize to 0-100 range
            position_max = np.max(position_heatmap)
            if position_max > 0:
                position_heatmap = (position_heatmap / position_max * 100).astype(int)
                
            click_max = np.max(click_heatmap)
            if click_max > 0:
                click_heatmap = (click_heatmap / click_max * 100).astype(int)
            
            # Convert to Python lists for JSON serialization
            position_list = position_heatmap.tolist()
            click_list = click_heatmap.tolist()
            
            return jsonify({
                'position_heatmap': position_list,
                'click_heatmap': click_list,
                'resolution': {
                    'width': width,
                    'height': height
                },
                'device_id': device_id,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error generating heatmap data: {e}")
            return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

    @app.route('/api/security/device_alerts/<device_id>', methods=['GET', 'OPTIONS'])
    @app.route_decorator.require_auth
    def get_device_security_alerts(device_id):
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
    @app.route_decorator.require_auth
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
            
    # Return the registered routes
    return [
        receive_security_alert,
        get_device_security_alerts,
        receive_iot_data,
        get_iot_data,
        get_iot_heatmap
    ]