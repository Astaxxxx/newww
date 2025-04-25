#!/usr/bin/env python3
"""
MQTT Subscriber for IoT Gaming Mouse Data
This script subscribes to MQTT topics for IoT gaming mouse data and stores it in the database
"""

import os
import json
import time
import logging
import paho.mqtt.client as mqtt
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='mqtt_subscriber.log'
)
logger = logging.getLogger('mqtt_subscriber')

# Database setup
Base = declarative_base()

class IoTDevice(Base):
    """Model for IoT devices"""
    __tablename__ = 'iot_devices'
    
    id = Column(Integer, primary_key=True)
    device_id = Column(String(50), unique=True, nullable=False)
    device_type = Column(String(50), default='mouse')
    status = Column(String(20), default='offline')
    last_active = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    metrics = relationship('IoTMetric', backref='device', lazy=True)
    security_events = relationship('IoTSecurityEvent', backref='device', lazy=True)

class IoTMetric(Base):
    """Model for IoT device metrics"""
    __tablename__ = 'iot_metrics'
    
    id = Column(Integer, primary_key=True)
    device_id = Column(String(50), ForeignKey('iot_devices.device_id'), nullable=False)
    session_id = Column(String(50), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Performance metrics
    clicks_per_second = Column(Integer, default=0)
    movements_count = Column(Integer, default=0)
    dpi = Column(Integer, default=0)
    polling_rate = Column(Integer, default=0)
    avg_click_distance = Column(Float, default=0.0)
    button_count = Column(Integer, default=0)
    
    # Status metrics
    battery_level = Column(Integer, default=100)
    connection_quality = Column(Integer, default=100)
    under_attack = Column(Boolean, default=False)
    attack_duration = Column(Integer, default=0)

class IoTSecurityEvent(Base):
    """Model for IoT security events"""
    __tablename__ = 'iot_security_events'
    
    id = Column(Integer, primary_key=True)
    device_id = Column(String(50), ForeignKey('iot_devices.device_id'), nullable=False)
    alert_type = Column(String(50), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(Text)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)

class MQTTSubscriber:
    """MQTT Subscriber for IoT Gaming Mouse Data"""
    
    def __init__(self, mqtt_broker="localhost", mqtt_port=1883, 
                 mqtt_topic_prefix="iot/gaming/mouse", db_uri=None):
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_topic_prefix = mqtt_topic_prefix
        self.db_uri = db_uri or 'sqlite:///iot_devices.db'
        self.running = False
        
        # Set up database
        self.engine = create_engine(self.db_uri)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
        # Initialize MQTT client
        self.client = mqtt.Client(client_id="server-subscriber")
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        
    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        if rc == 0:
            logger.info(f"Connected to MQTT broker at {self.mqtt_broker}:{self.mqtt_port}")
            
            # Subscribe to all IoT device topics
            client.subscribe(f"{self.mqtt_topic_prefix}/+/data", qos=1)
            client.subscribe(f"{self.mqtt_topic_prefix}/+/status", qos=1)
            client.subscribe(f"{self.mqtt_topic_prefix}/+/security", qos=2)
            
            logger.info(f"Subscribed to topics: {self.mqtt_topic_prefix}/+/data, /status, /security")
        else:
            logger.error(f"Failed to connect to MQTT broker with code: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from MQTT broker"""
        logger.warning(f"Disconnected from MQTT broker with code: {rc}")
        
        # Try to reconnect if we're still running
        if self.running:
            logger.info("Attempting to reconnect...")
            time.sleep(5)
            try:
                client.reconnect()
            except Exception as e:
                logger.error(f"Reconnection failed: {e}")
    
    def _on_message(self, client, userdata, msg):
        """Callback when message is received"""
        try:
            topic_parts = msg.topic.split('/')
            if len(topic_parts) >= 3:
                device_id = topic_parts[-2]
                message_type = topic_parts[-1]
                
                logger.debug(f"Received {message_type} message from {device_id}")
                
                payload = json.loads(msg.payload)
                
                # Process message based on type
                if message_type == 'data':
                    self._process_data_message(device_id, payload)
                elif message_type == 'status':
                    self._process_status_message(device_id, payload)
                elif message_type == 'security':
                    self._process_security_message(device_id, payload)
            
        except json.JSONDecodeError as e:
            logger.error(f"Malformed message payload: {e}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def _process_data_message(self, device_id, payload):
        """Process data message from device"""
        try:
            # Ensure device exists
            self._ensure_device_exists(device_id)
            
            # Create database session
            session = self.Session()
            
            try:
                # Parse timestamp
                timestamp = datetime.fromisoformat(payload.get('timestamp', datetime.utcnow().isoformat()))
                
                # Create new metric record
                metric = IoTMetric(
                    device_id=device_id,
                    session_id=payload.get('session_id', 'unknown'),
                    timestamp=timestamp,
                    clicks_per_second=payload.get('metrics', {}).get('clicks_per_second', 0),
                    movements_count=payload.get('metrics', {}).get('movements_count', 0),
                    dpi=payload.get('metrics', {}).get('dpi', 0),
                    polling_rate=payload.get('metrics', {}).get('polling_rate', 0),
                    avg_click_distance=payload.get('metrics', {}).get('avg_click_distance', 0.0),
                    button_count=payload.get('metrics', {}).get('button_count', 0),
                    battery_level=payload.get('status', {}).get('battery_level', 100),
                    connection_quality=payload.get('status', {}).get('connection_quality', 100),
                    under_attack=payload.get('status', {}).get('under_attack', False),
                    attack_duration=payload.get('status', {}).get('attack_duration', 0)
                )
                
                # Update device last active time
                device = session.query(IoTDevice).filter_by(device_id=device_id).first()
                if device:
                    device.last_active = timestamp
                    device.status = 'online'
                
                # Add and commit
                session.add(metric)
                session.commit()
                
                logger.debug(f"Stored metrics for device {device_id}")
                
            except Exception as e:
                session.rollback()
                logger.error(f"Database error processing data message: {e}")
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Error processing data message: {e}")
    
    def _process_status_message(self, device_id, payload):
        """Process status message from device"""
        try:
            # Create database session
            session = self.Session()
            
            try:
                # Parse timestamp
                timestamp = datetime.fromisoformat(payload.get('timestamp', datetime.utcnow().isoformat()))
                status = payload.get('status', 'unknown')
                
                # Update device status
                device = session.query(IoTDevice).filter_by(device_id=device_id).first()
                
                if not device:
                    # Create new device if it doesn't exist
                    device = IoTDevice(
                        device_id=device_id,
                        status=status,
                        last_active=timestamp
                    )
                    session.add(device)
                else:
                    device.status = status
                    device.last_active = timestamp
                
                session.commit()
                logger.info(f"Updated status for device {device_id}: {status}")
                
            except Exception as e:
                session.rollback()
                logger.error(f"Database error processing status message: {e}")
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Error processing status message: {e}")
    
    def _process_security_message(self, device_id, payload):
        """Process security message from device"""
        try:
            # Ensure device exists
            self._ensure_device_exists(device_id)
            
            # Create database session
            session = self.Session()
            
            try:
                # Parse timestamp
                timestamp = datetime.fromisoformat(payload.get('timestamp', datetime.utcnow().isoformat()))
                alert_type = payload.get('alert_type', 'unknown')
                details = json.dumps(payload.get('details', {}))
                
                if alert_type == 'attack_detected':
                    # Create new security event
                    event = IoTSecurityEvent(
                        device_id=device_id,
                        alert_type=alert_type,
                        timestamp=timestamp,
                        details=details,
                        resolved=False
                    )
                    session.add(event)
                    
                    logger.warning(f"Security alert from device {device_id}: {alert_type}")
                    
                elif alert_type == 'attack_resolved':
                    # Find and update unresolved events for this device
                    unresolved_events = session.query(IoTSecurityEvent).filter_by(
                        device_id=device_id,
                        alert_type='attack_detected',
                        resolved=False
                    ).all()
                    
                    for event in unresolved_events:
                        event.resolved = True
                        event.resolved_at = timestamp
                    
                    logger.info(f"Security alert resolved for device {device_id}")
                
                session.commit()
                
            except Exception as e:
                session.rollback()
                logger.error(f"Database error processing security message: {e}")
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Error processing security message: {e}")
    
    def _ensure_device_exists(self, device_id):
        """Ensure device exists in database"""
        session = self.Session()
        try:
            device = session.query(IoTDevice).filter_by(device_id=device_id).first()
            if not device:
                logger.info(f"Creating new device record for {device_id}")
                device = IoTDevice(
                    device_id=device_id,
                    status='unknown'
                )
                session.add(device)
                session.commit()
                
        except Exception as e:
            session.rollback()
            logger.error(f"Database error ensuring device exists: {e}")
        finally:
            session.close()
    
    def start(self):
        """Start the MQTT subscriber"""
        self.running = True
        
        # Connect to MQTT broker
        try:
            self.client.connect(self.mqtt_broker, self.mqtt_port, 60)
            self.client.loop_start()
            logger.info("MQTT subscriber started")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            self.running = False
            return False
    
    def stop(self):
        """Stop the MQTT subscriber"""
        if self.running:
            self.running = False
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("MQTT subscriber stopped")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='MQTT Subscriber for IoT Gaming Mouse Data')
    parser.add_argument('--broker', default='localhost', help='MQTT broker address')
    parser.add_argument('--port', type=int, default=1883, help='MQTT broker port')
    parser.add_argument('--topic', default='iot/gaming/mouse', help='MQTT topic prefix')
    parser.add_argument('--db', default='sqlite:///iot_devices.db', help='Database URI')
    args = parser.parse_args()
    
    try:
        subscriber = MQTTSubscriber(
            mqtt_broker=args.broker,
            mqtt_port=args.port,
            mqtt_topic_prefix=args.topic,
            db_uri=args.db
        )
        
        if subscriber.start():
            # Keep the main thread running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("Stopping subscriber...")
                subscriber.stop()
        else:
            print("Failed to start the subscriber")
                
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    main()