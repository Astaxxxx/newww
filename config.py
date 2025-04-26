#!/usr/bin/env python3
"""
Secure Esports Equipment Performance Tracker - Configuration Settings
"""

import os
import uuid
import socket
import hashlib
import base64
from cryptography.fernet import Fernet

# Server connection settings
SERVER_URL = "http://localhost:5000"  # Local development server

# Generate deterministic client ID from machine info for consistent identification
hostname = socket.gethostname()
mac_addresses = []

# Get MAC addresses for consistent device identification
try:
    import uuid
    from getmac import get_mac_address
    primary_mac = get_mac_address()
    if primary_mac:
        mac_addresses.append(primary_mac)
except:
    # Fallback if getmac is not available
    try:
        import netifaces
        interfaces = netifaces.interfaces()
        for interface in interfaces:
            try:
                mac = netifaces.ifaddresses(interface)[netifaces.AF_LINK][0]['addr']
                if mac and mac != '00:00:00:00:00:00':
                    mac_addresses.append(mac)
            except:
                pass
    except:
        # If all else fails, use a random UUID
        pass

# Create deterministic client ID
if mac_addresses:
    # Use first MAC address as seed
    id_seed = mac_addresses[0] + hostname
    client_id_hash = hashlib.sha256(id_seed.encode()).digest()
    CLIENT_ID = str(uuid.UUID(bytes=client_id_hash[:16]))
else:
    # Fallback to random UUID if no MAC found
    CLIENT_ID = str(uuid.uuid4())

# Generate client secret
key = Fernet.generate_key()
CLIENT_SECRET = base64.b64encode(key).decode('utf-8')

# Device identification
DEVICE_NAME = socket.gethostname()
DEVICE_TYPE = "Gaming PC"  # Customize as needed

# Application settings
DATA_DIR = os.path.join(os.path.expanduser("~"), ".secure-esports-tracker")
KEY_FILE = os.path.join(DATA_DIR, "encryption.key")
LOG_FILE = os.path.join(DATA_DIR, "agent.log")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Generate encryption key if it doesn't exist
if not os.path.exists(KEY_FILE):
    key = Fernet.generate_key()
    with open(KEY_FILE, 'wb') as key_file:
        key_file.write(key)
    # Set secure permissions (might not work on Windows)
    try:
        os.chmod(KEY_FILE, 0o600)
    except:
        pass  # Skip permission setting on Windows

# Security settings
TLS_VERIFY = True  # Always verify TLS certificates
DATA_RETENTION_DAYS = 30  # How long to keep data on server
PRIVACY_MODE = True  # When True, doesn't collect specific keys pressed, only metrics

# Save client ID and secret to a secure file
credentials_file = os.path.join(DATA_DIR, "credentials.dat")
if not os.path.exists(credentials_file):
    try:
        with open(credentials_file, 'w') as f:
            f.write(f"CLIENT_ID={CLIENT_ID}\n")
            f.write(f"CLIENT_SECRET={CLIENT_SECRET}\n")
        # Set secure permissions
        try:
            os.chmod(credentials_file, 0o600)
        except:
            pass  # Skip permission setting on Windows
    except Exception as e:
        print(f"Error saving credentials: {e}")

# Print configuration info for debugging
print(f"Client ID: {CLIENT_ID}")
print(f"Device Name: {DEVICE_NAME}")
print(f"Device Type: {DEVICE_TYPE}")
print(f"Data Directory: {DATA_DIR}")
print(f"Server URL: {SERVER_URL}")