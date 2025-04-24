#!/usr/bin/env python3
"""
Secure Esports Equipment Performance Tracker - Input Monitoring Agent
Captures keyboard and mouse inputs securely for performance analysis
"""

import time
import json
import uuid
import hashlib
import logging
import threading
import os
import socket
from datetime import datetime
from pynput import keyboard, mouse
from cryptography.fernet import Fernet
from secure_sender import SecureSender
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=config.LOG_FILE
)
logger = logging.getLogger('input_monitor')

class InputMonitor:
    """Securely monitors keyboard and mouse inputs for gaming performance analysis"""
    
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.start_time = datetime.now()
        self.keyboard_events = []
        self.mouse_events = []
        self.key_press_count = 0
        self.mouse_click_count = 0
        self.actions_per_minute = 0
        self.last_minute_actions = 0
        self.last_minute_time = time.time()
        self.offline_mode = False
        
        # Load encryption key
        try:
            with open(config.KEY_FILE, 'rb') as key_file:
                key = key_file.read()
                self.cipher = Fernet(key)
        except Exception as e:
            logger.error(f"Failed to load encryption key: {e}")
            raise
        
        # Setup secure sender
        self.sender = SecureSender(config.SERVER_URL, config.CLIENT_ID, config.CLIENT_SECRET)
        
        # Start APM calculation thread
        self.running = True
        self.apm_thread = threading.Thread(target=self._calculate_apm)
        self.apm_thread.daemon = True
        self.apm_thread.start()
        
        # Create data directory for offline storage
        os.makedirs(os.path.join(config.DATA_DIR, 'local_data'), exist_ok=True)
        
        # Add IoT device monitoring
        self.iot_devices = {}
        self.iot_thread = threading.Thread(target=self._monitor_iot_devices)
        self.iot_thread.daemon = True
        self.iot_thread.start()

        logger.info(f"Input monitoring session started: {self.session_id}")

    def start(self):
        """Start monitoring keyboard and mouse inputs"""
        # Check connection to server
        if not self.sender.test_connection():
            logger.warning("Server connection failed. Starting in offline mode.")
            self.offline_mode = True
            print("⚠️ Running in offline mode - data will be stored locally")
        else:
            self.offline_mode = False
            print("✅ Connected to server - data will be uploaded in real-time")
            
        # Keyboard listener
        self.keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release
        )
        self.keyboard_listener.start()
        
        # Mouse listener
        self.mouse_listener = mouse.Listener(
            on_move=self._on_mouse_move,
            on_click=self._on_mouse_click,
            on_scroll=self._on_mouse_scroll
        )
        self.mouse_listener.start()
        
        try:
            print(f"Input monitoring started. Press Ctrl+C to stop.")
            while self.running:
                # Send accumulated data every 10 seconds
                time.sleep(10)
                self._send_data()
                
                # Try to sync local data if we were previously offline
                if not self.offline_mode:
                    self.sender.sync_local_data()
        except KeyboardInterrupt:
            print("\nStopping input monitoring...")
            self.stop()
        except Exception as e:
            logger.error(f"Error in input monitor main loop: {e}")
            self.stop()

    def stop(self):
        """Stop monitoring and clean up"""
        self.running = False
        if hasattr(self, 'keyboard_listener'):
            self.keyboard_listener.stop()
        if hasattr(self, 'mouse_listener'):
            self.mouse_listener.stop()
            
        # Try to send final data, but don't get stuck if server is down
        try:
            self._send_data(final=True)  # Send final data
        except Exception as e:
            logger.error(f"Error sending final data: {e}")
        
        logger.info(f"Input monitoring session ended: {self.session_id}")
        print("Input monitoring stopped.")

    def _on_key_press(self, key):
        """Handle key press events"""
        try:
            # Record timestamp and key
            event = {
                'timestamp': time.time(),
                'event_type': 'press',
                'key': str(key) if not config.PRIVACY_MODE else 'key_press'
            }
            self.keyboard_events.append(event)
            self.key_press_count += 1
            self.last_minute_actions += 1
            
            # For security, don't log actual keys pressed
            logger.debug(f"Key press recorded (count: {self.key_press_count})")
        except Exception as e:
            logger.error(f"Error handling key press: {e}")

    def _on_key_release(self, key):
        """Handle key release events"""
        try:
            event = {
                'timestamp': time.time(),
                'event_type': 'release',
                'key': str(key) if not config.PRIVACY_MODE else 'key_release'
            }
            self.keyboard_events.append(event)
            logger.debug("Key release recorded")
        except Exception as e:
            logger.error(f"Error handling key release: {e}")

    def _on_mouse_move(self, x, y):
        """Handle mouse movement events (sampled to reduce volume)"""
        try:
            # Only sample some movements to reduce data volume
            if len(self.mouse_events) % 5 == 0:
                event = {
                    'timestamp': time.time(),
                    'event_type': 'move',
                    'x': x,
                    'y': y
                }
                self.mouse_events.append(event)
            logger.debug("Mouse move recorded")
        except Exception as e:
            logger.error(f"Error handling mouse move: {e}")

    def _on_mouse_click(self, x, y, button, pressed):
        """Handle mouse click events"""
        try:
            event = {
                'timestamp': time.time(),
                'event_type': 'click',
                'button': str(button),
                'pressed': pressed,
                'x': x,
                'y': y
            }
            self.mouse_events.append(event)
            if pressed:
                self.mouse_click_count += 1
                self.last_minute_actions += 1
            logger.debug(f"Mouse click recorded (count: {self.mouse_click_count})")
        except Exception as e:
            logger.error(f"Error handling mouse click: {e}")

    def _on_mouse_scroll(self, x, y, dx, dy):
        """Handle mouse scroll events"""
        try:
            event = {
                'timestamp': time.time(),
                'event_type': 'scroll',
                'x': x,
                'y': y,
                'dx': dx,
                'dy': dy
            }
            self.mouse_events.append(event)
            self.last_minute_actions += 1
            logger.debug("Mouse scroll recorded")
        except Exception as e:
            logger.error(f"Error handling mouse scroll: {e}")

    def _calculate_apm(self):
        """Calculate actions per minute in a separate thread"""
        while self.running:
            try:
                current_time = time.time()
                elapsed = current_time - self.last_minute_time
                
                if elapsed >= 60:
                    self.actions_per_minute = self.last_minute_actions
                    self.last_minute_actions = 0
                    self.last_minute_time = current_time
                    logger.info(f"Current APM: {self.actions_per_minute}")
                
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error calculating APM: {e}")

    def _send_data(self, final=False):
        """Encrypt and send collected data to the server"""
        try:
            if not (self.keyboard_events or self.mouse_events) and not final:
                return
            
            # Prepare data package
            data_package = {
                'session_id': self.session_id,
                'timestamp': datetime.now().isoformat(),
                'metrics': {
                    'key_press_count': self.key_press_count,
                    'mouse_click_count': self.mouse_click_count,
                    'actions_per_minute': self.actions_per_minute
                },
                'device_info': {
                    'client_id': config.CLIENT_ID,
                    'device_name': config.DEVICE_NAME,
                    'device_type': config.DEVICE_TYPE
                }
            }
            
            # Add data integrity hash
            data_string = json.dumps(data_package, sort_keys=True)
            data_package['integrity_hash'] = hashlib.sha256(data_string.encode()).hexdigest()
            
            # Encrypt data
            encrypted_data = self.cipher.encrypt(json.dumps(data_package).encode())
            
            # Send data to server
            response = self.sender.send_data(encrypted_data)
            
            if response and response.status_code == 200:
                logger.info("Data successfully sent to server")
                # Clear sent data to avoid duplication
                self.keyboard_events = []
                self.mouse_events = []
            elif not response and self.offline_mode:
                logger.info("Data stored locally (offline mode)")
                # Clear events since they've been stored locally
                self.keyboard_events = []
                self.mouse_events = []
            else:
                logger.warning(f"Failed to send data: {response}")
                
        except Exception as e:
            logger.error(f"Error sending data: {e}")

    def _monitor_iot_devices(self):
        """Monitor IoT gaming devices for metrics and attacks"""
        while self.running:
            try:
                # Listen for IoT device metrics on port 5000
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind(('localhost', 5000))
                sock.listen(5)
                
                while self.running:
                    client, addr = sock.accept()
                    data = client.recv(1024)
                    if data:
                        self._process_iot_data(data)
                    client.close()
                    
            except Exception as e:
                logger.error(f"Error monitoring IoT devices: {e}")
                time.sleep(5)  # Wait before retrying

    def _process_iot_data(self, data):
        """Process data received from IoT devices"""
        try:
            data = json.loads(data.decode())
            
            if 'attack_source' in data:
                # This is attack data
                logger.warning(f"Attack detected on {data['device_type']}: {data['packet_count']} packets from {data['attack_source']}")
                self._send_attack_data(data)
            else:
                # This is metrics data
                device_type = data['device_type']
                self.iot_devices[device_type] = data['metrics']
                logger.info(f"Received metrics from {device_type}: {data['metrics']}")
                
        except Exception as e:
            logger.error(f"Error processing IoT data: {e}")

    def _send_attack_data(self, attack_data):
        """Send attack data to server"""
        try:
            data_package = {
                'session_id': self.session_id,
                'timestamp': datetime.now().isoformat(),
                'attack_data': attack_data,
                'device_info': {
                    'client_id': config.CLIENT_ID,
                    'device_name': config.DEVICE_NAME,
                    'device_type': config.DEVICE_TYPE
                }
            }
            
            encrypted_data = self.cipher.encrypt(json.dumps(data_package).encode())
            self.sender.send_data(encrypted_data)
            
        except Exception as e:
            logger.error(f"Error sending attack data: {e}")

if __name__ == "__main__":
    try:
        monitor = InputMonitor()
        monitor.start()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        logger.critical(f"Fatal error in input monitor: {e}")
        print(f"Error: {e}")