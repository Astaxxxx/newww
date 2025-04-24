#!/usr/bin/env python3
"""
Secure Esports Equipment Performance Tracker - Secure Sender Module
Handles secure communication with the server
"""

import json
import time
import hmac
import base64
import logging
import hashlib
import requests
from datetime import datetime
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=config.LOG_FILE
)
logger = logging.getLogger('secure_sender')

class SecureSender:
    """Handles secure communication with the server"""
    
    def __init__(self, server_url, client_id, client_secret):
        """Initialize secure sender with server URL and authentication credentials"""
        self.server_url = server_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_token = None
        self.token_expiry = 0
        # Maximum retry attempts
        self.max_retries = 3
        # Flag for offline mode
        self.offline_mode = False
        logger.info("Secure sender initialized")
        
    def authenticate(self):
        """Authenticate with the server and get an access token"""
        if self.offline_mode:
            logger.info("Operating in offline mode, authentication skipped")
            return True
            
        try:
            timestamp = str(int(time.time()))
            
            # Prepare authentication data
            auth_data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'timestamp': timestamp,
                'device_type': config.DEVICE_TYPE,
                'device_name': config.DEVICE_NAME
            }
            
            # Create signature for authentication
            signature = hmac.new(
                self.client_secret.encode(),
                f"{self.client_id}:{timestamp}".encode(),
                hashlib.sha256
            ).hexdigest()
            
            auth_data['signature'] = signature
            
            try:
                response = requests.post(
                    f"{self.server_url}/api/auth/token",
                    json=auth_data,
                    headers={
                        'Content-Type': 'application/json',
                        'X-Client-ID': self.client_id
                    },
                    timeout=5,  # Short timeout to fail fast
                    verify=config.TLS_VERIFY
                )
                
                if response.status_code == 200:
                    auth_response = response.json()
                    self.auth_token = auth_response.get('token')
                    # Set expiry time from server response or default to 25 minutes
                    expires_in = auth_response.get('expires_in', 1500)
                    self.token_expiry = time.time() + expires_in
                    logger.info("Authentication successful")
                    self.offline_mode = False
                    return True
                else:
                    logger.error(f"Authentication failed: {response.status_code} - {response.text}")
                    return False
            except requests.exceptions.ConnectionError:
                logger.error(f"Cannot connect to server at {self.server_url}. Switching to offline mode.")
                self.offline_mode = True
                return False
            except requests.exceptions.Timeout:
                logger.error(f"Connection timeout to server at {self.server_url}. Switching to offline mode.")
                self.offline_mode = True
                return False
            except requests.exceptions.RequestException as e:
                logger.error(f"Network error: {e}. Switching to offline mode.")
                self.offline_mode = True
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            self.offline_mode = True
            return False
    
    def send_data(self, encrypted_data, retry_count=0):
        """Send encrypted data to the server with authentication"""
        # In offline mode, store data locally instead
        if self.offline_mode:
            self._store_data_locally(encrypted_data)
            return None
            
        try:
            # Check if token is expired or missing
            if not self.auth_token or time.time() > self.token_expiry:
                if not self.authenticate():
                    # If authentication fails, store data locally
                    logger.warning("Authentication failed, storing data locally")
                    self._store_data_locally(encrypted_data)
                    return None
            
            # Prepare data
            encoded_data = base64.b64encode(encrypted_data).decode('utf-8')
            
            # Create payload with metadata
            payload = {
                'data': encoded_data,
                'timestamp': datetime.now().isoformat(),
                'client_id': self.client_id,
                'data_type': 'performance_metrics'
            }
            
            # Create request signature
            request_data = json.dumps(payload, sort_keys=True)
            request_signature = hmac.new(
                self.client_secret.encode(),
                request_data.encode(),
                hashlib.sha256
            ).hexdigest()
            
            try:
                # Send data to server
                response = requests.post(
                    f"{self.server_url}/api/metrics/upload",
                    json=payload,
                    headers={
                        'Content-Type': 'application/json',
                        'X-Client-ID': self.client_id,
                        'X-Request-Signature': request_signature,
                        'Authorization': f"Bearer {self.auth_token}"
                    },
                    timeout=10,
                    verify=config.TLS_VERIFY
                )
                
                if response.status_code != 200:
                    logger.warning(f"Data upload failed: {response.status_code} - {response.text}")
                    
                    # Handle token expiration
                    if response.status_code == 401:
                        logger.info("Token expired, re-authenticating")
                        self.auth_token = None
                        if retry_count < self.max_retries:
                            return self.send_data(encrypted_data, retry_count + 1)
                        else:
                            logger.error("Max retries exceeded, storing data locally")
                            self._store_data_locally(encrypted_data)
                            return None
                    
                    # Store data locally for other errors
                    self._store_data_locally(encrypted_data)
                    return None
                
                logger.info("Data successfully sent to server")
                return response
                
            except requests.exceptions.ConnectionError:
                logger.error(f"Cannot connect to server at {self.server_url}. Storing data locally.")
                self._store_data_locally(encrypted_data)
                return None
            except requests.exceptions.Timeout:
                logger.error(f"Connection timeout to server. Storing data locally.")
                self._store_data_locally(encrypted_data)
                return None
            except requests.exceptions.RequestException as e:
                logger.error(f"Network error sending data: {e}. Storing data locally.")
                self._store_data_locally(encrypted_data)
                return None
        except Exception as e:
            logger.error(f"Error sending data: {e}")
            self._store_data_locally(encrypted_data)
            return None
    
    def _store_data_locally(self, encrypted_data):
        """Store data locally when server is unavailable"""
        try:
            import os
            import time
            
            # Create local data directory if it doesn't exist
            local_data_dir = os.path.join(config.DATA_DIR, 'local_data')
            os.makedirs(local_data_dir, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = int(time.time())
            filename = f"{timestamp}_{self.client_id}.dat"
            filepath = os.path.join(local_data_dir, filename)
            
            # Write encrypted data to file
            with open(filepath, 'wb') as f:
                f.write(encrypted_data)
                
            logger.info(f"Data stored locally: {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to store data locally: {e}")
    
    def sync_local_data(self):
        """Try to send locally stored data to the server"""
        if self.offline_mode:
            logger.info("Still in offline mode, skipping sync")
            return
            
        try:
            import os
            import glob
            
            local_data_dir = os.path.join(config.DATA_DIR, 'local_data')
            if not os.path.exists(local_data_dir):
                return
                
            # Find all locally stored data files
            data_files = glob.glob(os.path.join(local_data_dir, '*.dat'))
            if not data_files:
                return
                
            logger.info(f"Found {len(data_files)} locally stored data files to sync")
            
            # Try to authenticate first
            if not self.authenticate():
                logger.warning("Cannot authenticate to sync local data")
                return
                
            # Try to send each file
            for file_path in data_files:
                try:
                    with open(file_path, 'rb') as f:
                        encrypted_data = f.read()
                        
                    # Send to server
                    response = self.send_data(encrypted_data)
                    
                    if response and response.status_code == 200:
                        # If successful, delete the local file
                        os.remove(file_path)
                        logger.info(f"Successfully synced and removed: {file_path}")
                except Exception as e:
                    logger.error(f"Error syncing file {file_path}: {e}")
                    
        except Exception as e:
            logger.error(f"Error in sync_local_data: {e}")

    def test_connection(self):
        """Test connection to server and authentication"""
        try:
            logger.info(f"Testing connection to server: {self.server_url}")
            
            # Basic connectivity test
            try:
                response = requests.get(
                    self.server_url,
                    timeout=5,
                    verify=config.TLS_VERIFY
                )
                logger.info(f"Server connection successful: {response.status_code}")
            except requests.exceptions.RequestException as e:
                logger.error(f"Server connection failed: {e}")
                print(f"Cannot connect to server at {self.server_url}")
                print("Please check if the server is running and accessible.")
                return False
                
            # Authentication test
            if self.authenticate():
                logger.info("Authentication test successful")
                print("✓ Connection test successful!")
                print("✓ Authentication successful!")
                return True
            else:
                logger.error("Authentication test failed")
                print("✗ Authentication failed")
                return False
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            print(f"✗ Connection test failed: {e}")
            return False