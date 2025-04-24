#!/usr/bin/env python3
"""
Secure Esports Equipment Performance Tracker - Server Application
Flask-based server for receiving, processing, and analyzing equipment performance data
Enhanced with IoT device support and security alerts
"""

import os
import json
import hmac
import time
import uuid
import base64
import hashlib
import logging
import threading
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, request, jsonify, abort, render_template, Response, current_app
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='server.log'
)
logger = logging.getLogger('server')

# Create Flask application
app = Flask(__name__)

# Configure application
app.config['SECRET_KEY'] = 'secure-esports-tracker-secret-key'
app.config['DATABASE_PATH'] = os.getenv('DATABASE_PATH', 'secure_esports.db')
app.config['JWT_KEY'] = 'secure-esports-tracker-jwt-key-for-development'  # FIXED: Static key for development
app.config['CLIENT_SECRETS'] = {}  # Store client secrets (in memory for demonstration)

# Initialize storage for IoT data and alerts
app.iot_data = {}
app.device_alerts = {}

# Initialize CORS with more permissive settings for development
CORS(app, 
    resources={r"/*": {"origins": "*"}}, 
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Client-ID", "X-Request-Signature"],
    supports_credentials=True
)

# Add CORS headers to all responses
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,X-Client-ID,X-Request-Signature'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
    return response

# Simple in-memory data storage (replace with database in production)
users = {
    'admin': {
        'password': generate_password_hash('admin'),
        'role': 'admin'
    },
    'user': {
        'password': generate_password_hash('user'),
        'role': 'user'
    }
}

# Sample devices for demonstration purposes
devices = {
    'device_1': {
        'client_id': 'device_1',
        'client_secret': 'secret_1',
        'name': 'Gaming PC',
        'device_type': 'system',
        'status': 'active',
        'registered_at': datetime.utcnow().isoformat()
    },
    'device_2': {
        'client_id': 'device_2',
        'client_secret': 'secret_2',
        'name': 'Gaming Keyboard',
        'device_type': 'keyboard',
        'status': 'active',
        'registered_at': datetime.utcnow().isoformat()
    }
}

metrics = {}  # Will store performance metrics
sessions = {}  # Will store session data

# Security audit log
security_events = []

# Authentication decorator
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Handle OPTIONS requests directly for CORS preflight
        if request.method == 'OPTIONS':
            return '', 204
            
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            log_security_event('auth_failure', {'reason': 'missing_token', 'ip': request.remote_addr})
            return jsonify({'error': 'Authentication required'}), 401
            
        token = auth_header.split(' ')[1]
        
        try:
            # Debug: Log token
            logger.info(f"Decoding token: {token[:10]}...")
            
            payload = jwt.decode(token, app.config['JWT_KEY'], algorithms=['HS256'])
            request.user = payload
            
            # Debug: Log successful auth
            logger.info(f"Auth successful for user: {payload.get('sub')}")
        except jwt.ExpiredSignatureError:
            log_security_event('auth_failure', {'reason': 'expired_token'})
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError as e:
            log_security_event('auth_failure', {'reason': 'invalid_token', 'details': str(e)})
            return jsonify({'error': 'Invalid token', 'details': str(e)}), 401
        except Exception as e:
            log_security_event('auth_failure', {'reason': 'exception', 'details': str(e)})
            return jsonify({'error': 'Authentication error', 'details': str(e)}), 500
            
        return f(*args, **kwargs)
    return decorated

# Request signature verification decorator
def verify_signature(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Handle OPTIONS requests directly for CORS preflight
        if request.method == 'OPTIONS':
            return '', 204
            
        client_id = request.headers.get('X-Client-ID')
        signature = request.headers.get('X-Request-Signature')
        
        if not client_id or not signature:
            log_security_event('signature_failure', {'reason': 'missing_headers'})
            return jsonify({'error': 'Missing required headers'}), 400
            
        # Get client secret
        client_secret = app.config['CLIENT_SECRETS'].get(client_id)
        if not client_secret:
            if client_id in devices:
                client_secret = devices[client_id].get('client_secret')
                app.config['CLIENT_SECRETS'][client_id] = client_secret
            else:
                log_security_event('signature_failure', {'reason': 'unknown_client', 'client_id': client_id})
                return jsonify({'error': 'Unknown client'}), 401
            
        # Verify signature
        request_data = json.dumps(request.json, sort_keys=True)
        expected_signature = hmac.new(
            client_secret.encode(),
            request_data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            log_security_event('signature_failure', {'reason': 'invalid_signature', 'client_id': client_id})
            return jsonify({'error': 'Invalid signature'}), 401
            
        return f(*args, **kwargs)
    return decorated

# Security event logging
def log_security_event(event_type, details=None):
    timestamp = datetime.now().isoformat()
    
    event = {
        'timestamp': timestamp,
        'event_type': event_type,
        'ip_address': request.remote_addr if request else None,
        'details': details,
        'severity': 'warning' if event_type.startswith('auth_failure') or event_type.startswith('signature_failure') else 'info'
    }
    
    security_events.append(event)
    logger.info(f"SECURITY EVENT: {event_type} - {details}")

# --------- Routes ---------

@app.route('/')
def index():
    """Simple frontend for demonstration"""
    return """
    <html>
        <head>
            <title>Secure Esports Tracker</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                h1 { color: #333; }
            </style>
        </head>
        <body>
            <h1>Secure Esports Equipment Performance Tracker</h1>
            <p>Server is running. API endpoints available at /api/</p>
            <h2>Available endpoints:</h2>
            <ul>
                <li>/api/auth/login - User login</li>
                <li>/api/auth/token - Device authentication</li>
                <li>/api/auth/verify - Verify authentication token</li>
                <li>/api/metrics/upload - Upload performance metrics</li>
                <li>/api/analytics/performance - Get performance data</li>
                <li>/api/devices - Manage and view devices</li>
                <li>/api/sessions/recent - View recent sessions</li>
                <li>/api/security/logs - View security logs (admin only)</li>
                <li>/api/security/alert - Receive security alerts from IoT devices</li>
                <li>/api/security/device_alerts/:device_id - Get security alerts for a device</li>
                <li>/api/metrics/iot_data - Submit IoT device data</li>
                <li>/api/metrics/iot_data/:device_id - Get IoT device data</li>
            </ul>
        </body>
    </html>
    """

@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    """User login endpoint"""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        return '', 204
        
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
        
    user = users.get(username)
    
    if not user or not check_password_hash(user['password'], password):
        log_security_event('login_failure', {'username': username})
        return jsonify({'error': 'Invalid credentials'}), 401
        
    # Generate JWT token
    now = datetime.utcnow()
    token_data = {
        'sub': username,
        'role': user['role'],
        'iat': int(now.timestamp()),
        'exp': int((now + timedelta(hours=24)).timestamp())
    }
    
    # Debug: Print the key used for JWT encoding
    logger.info(f"JWT Key type: {type(app.config['JWT_KEY'])}")
    
    token = jwt.encode(token_data, app.config['JWT_KEY'], algorithm='HS256')
    
    # Debug: Log the token
    logger.info(f"Generated token: {token[:10]}...")
    
    log_security_event('login_success', {'username': username})
    
    return jsonify({
        'token': token,
        'user': {
            'username': username,
            'role': user['role']
        }
    })

@app.route('/api/auth/verify', methods=['GET', 'OPTIONS'])
def verify_token():
    """Verify authentication token and return user data"""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        return '', 204
        
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Authentication required'}), 401
        
    token = auth_header.split(' ')[1]
    
    try:
        # Debug: Log token being verified
        logger.info(f"Verifying token: {token[:10]}...")
        
        payload = jwt.decode(token, app.config['JWT_KEY'], algorithms=['HS256'])
        
        # Return user data
        username = payload.get('sub')
        role = payload.get('role', 'user')
        
        # Debug: Log successful verification
        logger.info(f"Token verification successful for user: {username}")
        
        return jsonify({
            'username': username,
            'role': role
        })
        
    except jwt.ExpiredSignatureError:
        log_security_event('token_verification', {'status': 'expired'})
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError as e:
        log_security_event('token_verification', {'status': 'invalid', 'details': str(e)})
        return jsonify({'error': 'Invalid token', 'details': str(e)}), 401
    except Exception as e:
        log_security_event('token_verification', {'status': 'error', 'details': str(e)})
        return jsonify({'error': 'Verification error', 'details': str(e)}), 500

@app.route('/api/auth/token', methods=['POST', 'OPTIONS'])
def get_token():
    """Generate authentication token for client"""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = request.json
        client_id = data.get('client_id')
        timestamp = data.get('timestamp')
        signature = data.get('signature')
        client_secret = data.get('client_secret')
        
        if not client_id or not timestamp:
            return jsonify({'error': 'Missing required parameters'}), 400
            
        # Check timestamp to prevent replay attacks (within 5 minutes)
        current_time = int(time.time())
        if abs(current_time - int(timestamp)) > 300:
            log_security_event('auth_failure', {'reason': 'timestamp_invalid', 'client_id': client_id})
            return jsonify({'error': 'Timestamp expired'}), 401
            
        # Find device
        device = devices.get(client_id)
        
        # If device doesn't exist, register it with client_secret
        if not device:
            if not client_secret:
                return jsonify({'error': 'Client secret required for registration'}), 400
                
            device = {
                'client_id': client_id,
                'client_secret': client_secret,
                'name': f"Device {client_id[:8]}",
                'status': 'active',
                'registered_at': datetime.utcnow().isoformat(),
                'device_type': data.get('device_type', 'unknown')
            }
            devices[client_id] = device
            app.config['CLIENT_SECRETS'][client_id] = client_secret
            log_security_event('device_registered', {'client_id': client_id})
        else:
            # If device exists but signature is required
            if signature:
                # Verify signature
                signature_data = f"{client_id}:{timestamp}"
                expected_signature = hmac.new(
                    device['client_secret'].encode(),
                    signature_data.encode(),
                    hashlib.sha256
                ).hexdigest()
                
                if not hmac.compare_digest(signature, expected_signature):
                    log_security_event('auth_failure', {'reason': 'signature_invalid', 'client_id': client_id})
                    return jsonify({'error': 'Invalid signature'}), 401
            
        # Generate token
        now = datetime.utcnow()
        token_data = {
            'sub': client_id,
            'type': 'device',
            'iat': int(now.timestamp()),
            'exp': int((now + timedelta(minutes=30)).timestamp())
        }
        
        token = jwt.encode(token_data, app.config['JWT_KEY'], algorithm='HS256')
        log_security_event('auth_success', {'client_id': client_id})
        
        return jsonify({
            'token': token,
            'expires_in': 1800  # 30 minutes
        })
        
    except Exception as e:
        logger.error(f"Error in token generation: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/metrics/upload', methods=['POST', 'OPTIONS'])
@require_auth
@verify_signature
def upload_metrics():
    """Receive encrypted metrics data from clients"""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = request.json
        client_id = data.get('client_id')
        encoded_data = data.get('data')
        
        if not client_id or not encoded_data:
            return jsonify({'error': 'Missing required parameters'}), 400
            
        # Decode base64 data
        encrypted_data = base64.b64decode(encoded_data)
        
        # Find device
        device = devices.get(client_id)
        if not device:
            return jsonify({'error': 'Unknown device'}), 401
            
        # Store encrypted data (in production, would decrypt and store in database)
        timestamp = datetime.utcnow().isoformat()
        if client_id not in metrics:
            metrics[client_id] = []
            
        metrics[client_id].append({
            'timestamp': timestamp,
            'encrypted_data': encrypted_data
        })
        
        # In production, would verify integrity and decrypt here
        
        log_security_event('data_received', {
            'client_id': client_id,
            'data_size': len(encoded_data)
        })
        
        return jsonify({'status': 'success'})
        
    except Exception as e:
        logger.error(f"Error processing metrics: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/analytics/performance', methods=['GET', 'OPTIONS'])
@require_auth
def get_performance():
    """Get performance analytics (simplified demo version)"""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        time_range = request.args.get('timeRange', 'day')
        
        # In a real implementation, would fetch and decrypt data from database
        # For demonstration, return sample data
        sample_data = [
            {
                'timestamp': (datetime.utcnow() - timedelta(minutes=50)).isoformat(),
                'actions_per_minute': 120,
                'key_press_count': 100,
                'mouse_click_count': 50
            },
            {
                'timestamp': (datetime.utcnow() - timedelta(minutes=40)).isoformat(),
                'actions_per_minute': 135,
                'key_press_count': 110,
                'mouse_click_count': 60
            },
            {
                'timestamp': (datetime.utcnow() - timedelta(minutes=30)).isoformat(),
                'actions_per_minute': 142,
                'key_press_count': 115,
                'mouse_click_count': 65
            },
            {
                'timestamp': (datetime.utcnow() - timedelta(minutes=20)).isoformat(),
                'actions_per_minute': 128,
                'key_press_count': 105,
                'mouse_click_count': 55
            },
            {
                'timestamp': (datetime.utcnow() - timedelta(minutes=10)).isoformat(),
                'actions_per_minute': 138,
                'key_press_count': 112,
                'mouse_click_count': 58
            }
        ]
        
        return jsonify({'data': sample_data})
        
    except Exception as e:
        logger.error(f"Error retrieving performance data: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/security/logs', methods=['GET', 'OPTIONS'])
@require_auth
def get_security_logs():
    """Get security logs (admin only)"""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        # Check if user is admin
        if request.user.get('role') != 'admin':
            log_security_event('access_denied', {'endpoint': 'security/logs'})
            return jsonify({'error': 'Admin access required'}), 403
            
        # Filter logs by severity if requested
        severity = request.args.get('severity', 'all')
        
        if severity == 'all':
            filtered_logs = security_events
        else:
            filtered_logs = [log for log in security_events if log.get('severity') == severity]
            
        return jsonify({'logs': filtered_logs})
        
    except Exception as e:
        logger.error(f"Error retrieving security logs: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/devices', methods=['GET', 'OPTIONS'])
@require_auth
def get_devices():
    """Get registered devices"""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        return '', 204
        
    # Debug: Log request details
    logger.info(f"Devices request received from IP: {request.remote_addr}")
    logger.info(f"Headers: {dict(request.headers)}")
    
    try:
        # Always show sample devices
        user_devices = []
        for device_id, device in devices.items():
            # Remove sensitive information
            device_info = {
                'client_id': device_id,
                'name': device.get('name', f"Device {device_id[:8]}"),
                'device_type': device.get('device_type', 'unknown'),
                'status': device.get('status', 'active'),
                'registered_at': device.get('registered_at', datetime.utcnow().isoformat())
            }
            user_devices.append(device_info)
        
        logger.info(f"Returning {len(user_devices)} devices")
        return jsonify({'devices': user_devices})
        
    except Exception as e:
        logger.error(f"Error retrieving devices: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/devices/register', methods=['POST', 'OPTIONS'])
@require_auth
def register_device():
    """Register a new device"""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = request.json
        device_name = data.get('name')
        device_type = data.get('device_type', 'unknown')
        
        if not device_name:
            return jsonify({'error': 'Device name is required'}), 400
            
        # Generate device credentials
        client_id = str(uuid.uuid4())
        client_secret = base64.b64encode(os.urandom(32)).decode('utf-8')
        
        # Store device
        devices[client_id] = {
            'client_id': client_id,
            'client_secret': client_secret,
            'name': device_name,
            'device_type': device_type,
            'status': 'active',
            'registered_at': datetime.utcnow().isoformat()
        }
        
        log_security_event('device_registered', {
            'client_id': client_id,
            'device_name': device_name,
            'device_type': device_type
        })
        
        # Return device credentials
        return jsonify({
            'client_id': client_id,
            'client_secret': client_secret,
            'name': device_name,
            'device_type': device_type,
            'status': 'active'
        })
        
    except Exception as e:
        logger.error(f"Error registering device: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/sessions/recent', methods=['GET', 'OPTIONS'])
@require_auth
def get_recent_sessions():
    """Get recent sessions with performance data"""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        filter_type = request.args.get('filter', 'all')
        
        # In a real implementation, would fetch from database
        # For demonstration, return sample data
        recent_sessions = [
            {
                'id': '1',
                'start_time': (datetime.utcnow() - timedelta(days=1)).isoformat(),
                'duration_minutes': 120,
                'average_apm': 130,
                'device_name': 'Gaming PC'
            },
            {
                'id': '2',
                'start_time': (datetime.utcnow() - timedelta(hours=12)).isoformat(),
                'duration_minutes': 90,
                'average_apm': 145,
                'device_name': 'Gaming PC'
            },
            {
                'id': '3',
                'start_time': (datetime.utcnow() - timedelta(hours=4)).isoformat(),
                'duration_minutes': 60,
                'average_apm': 138,
                'device_name': 'Gaming PC'
            }
        ]
        
        # Filter sessions based on time if needed
        if filter_type == 'week':
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_sessions = [s for s in recent_sessions if datetime.fromisoformat(s['start_time']) > week_ago]
        elif filter_type == 'month':
            month_ago = datetime.utcnow() - timedelta(days=30)
            recent_sessions = [s for s in recent_sessions if datetime.fromisoformat(s['start_time']) > month_ago]
        
        return jsonify({'sessions': recent_sessions})
        
    except Exception as e:
        logger.error(f"Error retrieving recent sessions: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/devices/stats', methods=['GET', 'OPTIONS'])
@require_auth
def get_device_stats():
    """Get device usage statistics"""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        # In a real implementation, would calculate from database
        # For demonstration, return sample data
        device_stats = [
            {
                'device_name': 'Gaming PC',
                'usage_percentage': 0.75,
                'average_apm': 135,
                'total_sessions': 12
            },
            {
                'device_name': 'Laptop',
                'usage_percentage': 0.25,
                'average_apm': 110,
                'total_sessions': 4
            }
        ]
        
        return jsonify({'devices': device_stats})
        
    except Exception as e:
        logger.error(f"Error retrieving device statistics: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/users/settings', methods=['PUT', 'OPTIONS'])
@require_auth
def update_user_settings():
    """Update user settings"""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = request.json
        username = request.user.get('sub')
        
        # In a real implementation, would update in database
        # For demonstration, just return success
        
        return jsonify({'status': 'success', 'message': 'Settings updated'})
        
    except Exception as e:
        logger.error(f"Error updating user settings: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

# === NEW IOT ROUTES AND SECURITY ALERT ROUTES ===

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
        security_events.append({
            'timestamp': datetime.now().isoformat(),
            'event_type': f'iot_{event_type}',
            'ip_address': request.remote_addr,
            'details': details,
            'severity': severity
        })
        
        # Add to device-specific alerts list
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
        if device_id not in app.device_alerts:
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
        if device_id not in app.iot_data:
            return jsonify({'data': []})
            
        return jsonify({'data': app.iot_data[device_id]})
        
    except Exception as e:
        logger.error(f"Error retrieving IoT data: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

# ------- Main application entry point -------

if __name__ == '__main__':
    print("Starting Secure Esports Equipment Performance Tracker Server...")
    print("Server available at http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)