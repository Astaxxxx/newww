#!/usr/bin/env python3
"""
Secure Esports Equipment Performance Tracker - Database Models
"""

import os
import uuid
import hashlib
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication and access control"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'user', 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    active = db.Column(db.Boolean, default=True)
    
    # Relationships
    devices = db.relationship('Device', backref='owner', lazy=True)
    
    def set_password(self, password):
        """Set user password with secure hashing"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256:150000')
        
    def check_password(self, password):
        """Verify password against stored hash"""
        return check_password_hash(self.password_hash, password)
        
    def __repr__(self):
        return f'<User {self.username}>'

class Device(db.Model):
    """Device model for tracking registered gaming peripherals"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    client_id = db.Column(db.String(36), unique=True, nullable=False)
    client_secret = db.Column(db.String(64), nullable=False)
    encryption_key = db.Column(db.String(64), nullable=False, default=lambda: os.urandom(32).hex())
    name = db.Column(db.String(100), nullable=False)
    device_type = db.Column(db.String(50))  # e.g., 'keyboard', 'mouse', 'system'
    status = db.Column(db.String(20), default='pending')  # 'pending', 'active', 'disabled'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime)
    
    # Relationships
    sessions = db.relationship('Session', backref='device', lazy=True)
    
    def __repr__(self):
        return f'<Device {self.name} ({self.client_id[:8]})>'

class Session(db.Model):
    """Gaming session model for tracking performance periods"""
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), unique=True, nullable=False)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=True)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    duration_seconds = db.Column(db.Integer)
    
    # Relationships
    metrics = db.relationship('PerformanceMetric', backref='session', lazy=True)
    
    def __repr__(self):
        return f'<Session {self.session_id[:8]}>'
        
    def calculate_duration(self):
        """Calculate session duration if end_time is set"""
        if self.end_time and self.start_time:
            delta = self.end_time - self.start_time
            self.duration_seconds = int(delta.total_seconds())
        return self.duration_seconds

class Game(db.Model):
    """Game model for tracking different games being played"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50))
    publisher = db.Column(db.String(100))
    
    # Relationships
    sessions = db.relationship('Session', backref='game', lazy=True)
    
    def __repr__(self):
        return f'<Game {self.name}>'

class PerformanceMetric(db.Model):
    """Performance metrics collected during gaming sessions"""
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Basic metrics
    key_press_count = db.Column(db.Integer, default=0)
    mouse_click_count = db.Column(db.Integer, default=0)
    actions_per_minute = db.Column(db.Integer, default=0)
    
    # Advanced metrics (optional)
    average_response_time_ms = db.Column(db.Float)
    key_hold_duration_ms = db.Column(db.Float)
    mouse_travel_distance_px = db.Column(db.Float)
    
    def __repr__(self):
        return f'<Metric {self.id} - APM: {self.actions_per_minute}>'

class SecurityEvent(db.Model):
    """Security audit log for tracking security-related events"""
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    event_type = db.Column(db.String(50), nullable=False)  # 'login', 'auth_failure', 'data_access', etc.
    ip_address = db.Column(db.String(45))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=True)
    details = db.Column(db.Text)
    severity = db.Column(db.String(20), default='info')  # 'info', 'warning', 'critical'
    
    def __repr__(self):
        return f'<SecurityEvent {self.id} - {self.event_type}>'