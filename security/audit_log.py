#!/usr/bin/env python3
"""
Secure Esports Equipment Performance Tracker - Security Audit Logger
Provides comprehensive security event logging functionality
"""

import os
import json
import time
import logging
import threading
from datetime import datetime
from flask import request, current_app

from database.models import db, SecurityEvent, User, Device

logger = logging.getLogger('security.audit')

class AuditLogger:
    """Handles security event logging and storage"""
    
    def __init__(self):
        """Initialize the audit logger"""
        self.log_queue = []
        self.queue_lock = threading.Lock()
        
        # Start background thread for flushing logs to database
        self.running = True
        self.flush_thread = threading.Thread(target=self._background_flush)
        self.flush_thread.daemon = True
        self.flush_thread.start()
        
        logger.info("Audit Logger initialized")
        
    def log_event(self, event_type, details=None, user_id=None, device_id=None, severity='info'):
        """Log a security event with relevant details"""
        try:
            timestamp = datetime.utcnow()
            
            # Get IP address from request if available
            ip_address = None
            if request:
                ip_address = request.remote_addr
                if request.headers.get('X-Forwarded-For'):
                    ip_address = request.headers.get('X-Forwarded-For').split(',')[0].strip()
            
            # Convert details dict to string if needed
            details_str = None
            if details:
                if isinstance(details, dict):
                    # Filter out any sensitive fields
                    filtered_details = {k: v for k, v in details.items() 
                                       if k.lower() not in ['password', 'token', 'secret', 'key']}
                    details_str = json.dumps(filtered_details)
                else:
                    details_str = str(details)
            
            # Create event record
            event = {
                'timestamp': timestamp,
                'event_type': event_type,
                'ip_address': ip_address,
                'user_id': user_id,
                'device_id': device_id,
                'details': details_str,
                'severity': severity
            }
            
            # Add to queue for batch processing
            with self.queue_lock:
                self.log_queue.append(event)
            
            # Log to console/file as well
            log_message = f"SECURITY EVENT: {event_type} | {severity.upper()} | {details_str}"
            if severity == 'critical':
                logger.critical(log_message)
            elif severity == 'warning':
                logger.warning(log_message)
            else:
                logger.info(log_message)
                
            # Immediately flush critical events
            if severity == 'critical':
                self.flush_logs()
                
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")
    
    def flush_logs(self):
        """Flush pending log events to the database"""
        try:
            with self.queue_lock:
                if not self.log_queue:
                    return 0
                    
                events_to_process = self.log_queue.copy()
                self.log_queue = []
                
            # Process events outside of lock to minimize lock time
            with current_app.app_context():
                for event in events_to_process:
                    security_event = SecurityEvent(
                        timestamp=event['timestamp'],
                        event_type=event['event_type'],
                        ip_address=event['ip_address'],
                        user_id=event['user_id'],
                        device_id=event['device_id'],
                        details=event['details'],
                        severity=event['severity']
                    )
                    db.session.add(security_event)
                
                db.session.commit()
                
            return len(events_to_process)
            
        except Exception as e:
            logger.error(f"Failed to flush security events to database: {e}")
            # Put events back in queue
            with self.queue_lock:
                self.log_queue = events_to_process + self.log_queue
            return 0
    
    def _background_flush(self):
        """Background thread that periodically flushes logs to database"""
        while self.running:
            try:
                time.sleep(10)  # Flush every 10 seconds
                with self.queue_lock:
                    if self.log_queue:
                        self.flush_logs()
            except Exception as e:
                logger.error(f"Error in background flush thread: {e}")
    
    def stop(self):
        """Stop the background flush thread and flush remaining logs"""
        self.running = False
        if self.flush_thread.is_alive():
            self.flush_thread.join(timeout=5)
        self.flush_logs()
    
    def get_recent_events(self, count=100, severity=None, event_type=None):
        """Retrieve recent security events with optional filtering"""
        try:
            with current_app.app_context():
                query = SecurityEvent.query
                
                if severity:
                    query = query.filter_by(severity=severity)
                    
                if event_type:
                    query = query.filter_by(event_type=event_type)
                    
                events = query.order_by(SecurityEvent.timestamp.desc()).limit(count).all()
                
                result = []
                for event in events:
                    result.append({
                        'id': event.id,
                        'timestamp': event.timestamp.isoformat(),
                        'event_type': event.event_type,
                        'ip_address': event.ip_address,
                        'user_id': event.user_id,
                        'device_id': event.device_id,
                        'details': event.details,
                        'severity': event.severity
                    })
                    
                return result
                
        except Exception as e:
            logger.error(f"Failed to retrieve security events: {e}")
            return []
    
    def get_events_by_user(self, user_id, count=100):
        """Retrieve security events for a specific user"""
        try:
            with current_app.app_context():
                events = SecurityEvent.query.filter_by(user_id=user_id) \
                    .order_by(SecurityEvent.timestamp.desc()) \
                    .limit(count).all()
                
                result = []
                for event in events:
                    result.append({
                        'id': event.id,
                        'timestamp': event.timestamp.isoformat(),
                        'event_type': event.event_type,
                        'ip_address': event.ip_address,
                        'details': event.details,
                        'severity': event.severity
                    })
                    
                return result
                
        except Exception as e:
            logger.error(f"Failed to retrieve user security events: {e}")
            return []
    
    def get_events_by_device(self, device_id, count=100):
        """Retrieve security events for a specific device"""
        try:
            with current_app.app_context():
                events = SecurityEvent.query.filter_by(device_id=device_id) \
                    .order_by(SecurityEvent.timestamp.desc()) \
                    .limit(count).all()
                
                result = []
                for event in events:
                    result.append({
                        'id': event.id,
                        'timestamp': event.timestamp.isoformat(),
                        'event_type': event.event_type,
                        'ip_address': event.ip_address,
                        'details': event.details,
                        'severity': event.severity
                    })
                    
                return result
                
        except Exception as e:
            logger.error(f"Failed to retrieve device security events: {e}")
            return []
            
    def summary_by_event_type(self, days=7):
        """Get summary of events by type over a period of days"""
        try:
            with current_app.app_context():
                from sqlalchemy import func
                from datetime import datetime, timedelta
                
                start_date = datetime.utcnow() - timedelta(days=days)
                
                summary = db.session.query(
                    SecurityEvent.event_type,
                    func.count(SecurityEvent.id).label('count')
                ).filter(
                    SecurityEvent.timestamp >= start_date
                ).group_by(
                    SecurityEvent.event_type
                ).all()
                
                result = {}
                for event_type, count in summary:
                    result[event_type] = count
                    
                return result
                
        except Exception as e:
            logger.error(f"Failed to retrieve security event summary: {e}")
            return {}