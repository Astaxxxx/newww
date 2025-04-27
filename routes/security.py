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
    @app.route_decorator.require_auth
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


    @app.route('/api/metrics/mouse_contact_heatmap/<device_id>', methods=['GET', 'OPTIONS'])
    @app.route_decorator.require_auth
    def get_mouse_contact_heatmap(device_id):
        """Get detailed contact and pressure data from the mouse IoT sensors"""
        # Handle OPTIONS request for CORS preflight
        if request.method == 'OPTIONS':
            return '', 204
            
        try:
            # In production, this would query a database for real sensor data
            # For this demo, we'll generate simulated data based on device_id for consistency
            
            # Use device_id as a seed for random data generation to ensure consistent results
            import hashlib
            import numpy as np
            import time
            
            # Create a seed from the device_id
            seed = int(hashlib.md5(device_id.encode()).hexdigest(), 16) % 10000
            np.random.seed(seed)
            
            # Add some time variation to avoid completely static data
            current_time = int(time.time() / 300)  # Changes every 5 minutes
            np.random.seed(seed + current_time)
            
            # Contact points heatmap (0-100 intensity scale)
            contact_points = {
                # Top surface (main clicks)
                'top_left': np.random.randint(80, 95),     # Index finger position (left click)
                'top_right': np.random.randint(65, 80),    # Middle finger position (right click)
                'top_middle': np.random.randint(40, 60),   # Area between buttons
                
                # Side surfaces
                'left_front': np.random.randint(75, 90),   # Thumb front position
                'left_back': np.random.randint(55, 75),    # Thumb back position
                'left_bottom': np.random.randint(45, 65),  # Lower thumb rest area
                'right_side': np.random.randint(20, 40),   # Right side of mouse (pinky area)
                
                # Bottom contact areas
                'palm_rest': np.random.randint(70, 90),    # Palm contact area
                'wrist_area': np.random.randint(40, 60),   # Wrist contact point
            }
            
            # Pressure data (0-100 scale)
            pressure = {
                'top_left': np.random.randint(80, 95),     # Left click pressure
                'top_right': np.random.randint(65, 85),    # Right click pressure
                'left_front': np.random.randint(85, 95),   # Thumb pressure (side buttons)
                'palm_rest': np.random.randint(55, 75),    # Palm pressure
            }
            
            # Click count data
            base_clicks = np.random.randint(3000, 8000)
            click_data = {
                'left_click': base_clicks,                      # Count of left clicks
                'right_click': int(base_clicks * 0.35),         # Count of right clicks
                'middle_click': int(base_clicks * 0.07),        # Count of middle clicks
                'side_button_1': int(base_clicks * 0.15),       # Count of side button 1 clicks
                'side_button_2': int(base_clicks * 0.2)         # Count of side button 2 clicks
            }
            
            # Finger position data
            finger_position = {
                'index_finger': {
                    'x_offset': np.random.randint(-3, 4),      # Lateral position offset in mm
                    'y_offset': np.random.randint(-5, 3),      # Forward/backward position offset
                    'angle': np.random.randint(8, 15)          # Finger angle in degrees
                },
                'middle_finger': {
                    'x_offset': np.random.randint(-2, 3),
                    'y_offset': np.random.randint(-2, 6),
                    'angle': np.random.randint(5, 12)
                },
                'thumb': {
                    'x_offset': np.random.randint(2, 8),
                    'y_offset': np.random.randint(3, 10),
                    'angle': np.random.randint(15, 25)
                }
            }
            
            # Generate posture issues based on the data
            posture_issues = []
            
            # Check thumb position
            if finger_position['thumb']['x_offset'] > 6 or finger_position['thumb']['y_offset'] > 8:
                posture_issues.append({
                    'issue': 'thumb_overextension',
                    'severity': 'high' if finger_position['thumb']['x_offset'] > 7 else 'medium',
                    'description': 'Your thumb is stretched too far to reach the side buttons'
                })
                
            # Check index finger angle
            if finger_position['index_finger']['angle'] > 12:
                posture_issues.append({
                    'issue': 'finger_overextension',
                    'severity': 'medium',
                    'description': 'Your index finger is at an awkward angle when clicking'
                })
                
            # Check pressure levels
            if pressure['top_left'] > 90:
                posture_issues.append({
                    'issue': 'excessive_click_pressure',
                    'severity': 'high',
                    'description': 'You are pressing the left mouse button with excessive force'
                })
                
            # Add a simulated wrist issue for some device IDs
            if device_id.endswith('1'):
                posture_issues.append({
                    'issue': 'excessive_wrist_extension',
                    'severity': 'medium',
                    'description': 'Your wrist is extended upward too much'
                })
            
            # Compile all data into a response object
            response_data = {
                'device_id': device_id,
                'contact_points': contact_points,
                'pressure': pressure,
                'click_data': click_data,
                'finger_position': finger_position,
                'posture_issues': posture_issues,
                'timestamp': datetime.now().isoformat(),
                'sensor_type': 'force_sensitive_resistors',
                'sensor_resolution': '12-bit (4096 levels)',
                'firmware_version': '2.1.4'
            }
            
            return jsonify(response_data)
        
        except Exception as e:
            logger.error(f"Error generating mouse contact heatmap data: {e}")
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