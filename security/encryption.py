#!/usr/bin/env python3
"""
Secure Esports Equipment Performance Tracker - Encryption Utilities
Provides encryption/decryption functions for secure data handling
"""

import os
import base64
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger('security.encryption')

def generate_key():
    """Generate a secure encryption key"""
    return Fernet.generate_key()

def derive_key(password, salt=None):
    """Derive a key from a password using PBKDF2"""
    if salt is None:
        salt = os.urandom(16)
        
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000
    )
    
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt

def encrypt_data(data, key):
    """Encrypt data using Fernet symmetric encryption"""
    if isinstance(data, str):
        data = data.encode('utf-8')
        
    try:
        cipher = Fernet(key)
        encrypted_data = cipher.encrypt(data)
        return encrypted_data
    except Exception as e:
        logger.error(f"Encryption error: {e}")
        raise

def decrypt_data(encrypted_data, key):
    """Decrypt data using Fernet symmetric encryption"""
    try:
        cipher = Fernet(key)
        decrypted_data = cipher.decrypt(encrypted_data)
        return decrypted_data.decode('utf-8')
    except Exception as e:
        logger.error(f"Decryption error: {e}")
        raise

def encrypt_sensitive_value(value, key):
    """Encrypt a sensitive value for storage"""
    if not value:
        return None
        
    if isinstance(value, str):
        value = value.encode('utf-8')
        
    try:
        cipher = Fernet(key)
        encrypted = cipher.encrypt(value)
        return base64.urlsafe_b64encode(encrypted).decode('utf-8')
    except Exception as e:
        logger.error(f"Failed to encrypt sensitive value: {e}")
        raise

def decrypt_sensitive_value(encrypted_value, key):
    """Decrypt a sensitive value from storage"""
    if not encrypted_value:
        return None
        
    try:
        encrypted_data = base64.urlsafe_b64decode(encrypted_value)
        cipher = Fernet(key)
        decrypted = cipher.decrypt(encrypted_data)
        return decrypted.decode('utf-8')
    except Exception as e:
        logger.error(f"Failed to decrypt sensitive value: {e}")
        raise
        
def rotate_key(old_key, data_to_reencrypt=None):
    """Generate a new key and re-encrypt data with it"""
    new_key = generate_key()
    
    if data_to_reencrypt:
        # Decrypt with old key
        decrypted = decrypt_data(data_to_reencrypt, old_key)
        
        # Re-encrypt with new key
        reencrypted = encrypt_data(decrypted, new_key)
        
        return new_key, reencrypted
    
    return new_key