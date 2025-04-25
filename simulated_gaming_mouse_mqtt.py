import time
import random
import json
import threading
import argparse
import paho.mqtt.client as mqtt
from datetime import datetime

class SimulatedGamingMouse:
    """Simulates an IoT gaming mouse that sends performance data via MQTT"""
    
    def __init__(self, device_id="mouse-001", mqtt_broker="localhost", mqtt_port=1883, 
                 mqtt_topic_prefix="iot/gaming/mouse", send_interval=1):
        self.device_id = device_id
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_topic_prefix = mqtt_topic_prefix
        self.send_interval = send_interval
        self.dpi = 16000
        self.polling_rate = 1000  # Hz
        self.button_count = 8
        self.running = False
        self.session_id = None
        
        # Performance metrics
        self.clicks_per_second = 0
        self.movement_data = []
        self.connected = False
        
        # Attack detection settings - using simulation instead of raw sockets
        self.ping_count = 0
        self.ping_threshold = 50  # Pings per second before considered an attack
        self.under_attack = False
        self.attack_start_time = None
        
        # Initialize MQTT client
        self.client = mqtt.Client(client_id=f"simulated-{self.device_id}")
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        
        # Set up MQTT topics
        self.data_topic = f"{self.mqtt_topic_prefix}/{self.device_id}/data"
        self.status_topic = f"{self.mqtt_topic_prefix}/{self.device_id}/status"
        self.security_topic = f"{self.mqtt_topic_prefix}/{self.device_id}/security"
        self.control_topic = f"{self.mqtt_topic_prefix}/{self.device_id}/control"
        
    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        if rc == 0:
            print(f"Connected to MQTT broker at {self.mqtt_broker}:{self.mqtt_port}")
            self.connected = True
            
            # Subscribe to control topic to receive commands
            self.client.subscribe(self.control_topic)
            self.client.on_message = self._on_message
            
            # Send initial status message
            self._publish_status("online")
        else:
            print(f"Failed to connect to MQTT broker with code: {rc}")
            self.connected = False
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from MQTT broker"""
        print(f"Disconnected from MQTT broker with code: {rc}")
        self.connected = False
    
    def _on_message(self, client, userdata, msg):
        """Callback when message is received"""
        try:
            payload = json.loads(msg.payload)
            if msg.topic == self.control_topic:
                self._handle_control_message(payload)
        except json.JSONDecodeError:
            print(f"Received malformed message: {msg.payload}")
        except Exception as e:
            print(f"Error processing message: {e}")
    
    def _handle_control_message(self, payload):
        """Handle control messages from server"""
        if 'command' in payload:
            command = payload['command']
            print(f"Received command: {command}")
            
            if command == 'set_dpi':
                if 'value' in payload:
                    self.dpi = payload['value']
                    print(f"DPI set to {self.dpi}")
                    self._publish_status("dpi_changed")
            
            elif command == 'set_polling_rate':
                if 'value' in payload:
                    self.polling_rate = payload['value']
                    print(f"Polling rate set to {self.polling_rate} Hz")
                    self._publish_status("polling_rate_changed")
            
            elif command == 'restart':
                print("Restarting device...")
                self._publish_status("restarting")
                self.stop()
                time.sleep(2)
                self.start()
    
    def start(self):
        """Start the simulated mouse"""
        self.running = True
        self.session_id = f"session_{int(time.time())}"
        
        # Connect to MQTT broker
        try:
            self.client.connect(self.mqtt_broker, self.mqtt_port, 60)
            self.client.loop_start()
        except Exception as e:
            print(f"Failed to connect to MQTT broker: {e}")
            return False
        
        # Start the main thread
        self.main_thread = threading.Thread(target=self._run)
        self.main_thread.daemon = True
        self.main_thread.start()
        
        # Start network monitoring thread
        self.network_thread = threading.Thread(target=self._monitor_network)
        self.network_thread.daemon = True
        self.network_thread.start()
        
        print(f"Simulated gaming mouse started with ID: {self.device_id}")
        print(f"Session ID: {self.session_id}")
        print(f"Simulating network traffic and attack detection...")
        return True
        
    def stop(self):
        """Stop the simulated mouse"""
        if self.running:
            self.running = False
            
            # Publish offline status
            if self.connected:
                self._publish_status("offline")
                
            # Stop MQTT client
            self.client.loop_stop()
            self.client.disconnect()
            
            # Wait for threads to complete
            if hasattr(self, 'main_thread') and self.main_thread.is_alive():
                self.main_thread.join(timeout=2)
            if hasattr(self, 'network_thread') and self.network_thread.is_alive():
                self.network_thread.join(timeout=2)
                
            print("Simulated gaming mouse stopped")
        
    def _generate_performance_data(self):
        """Generate simulated performance data"""
        # Generate random mouse clicks based on time of day (to simulate player activity)
        hour = datetime.now().hour
        if 9 <= hour <= 22:  # Gaming hours
            self.clicks_per_second = random.randint(1, 6)
        else:  # Non-gaming hours
            self.clicks_per_second = random.randint(0, 2)
            
        # Generate mouse movement data (x, y coordinates)
        for _ in range(self.clicks_per_second):
            self.movement_data.append({
                'x': random.randint(0, 1920),
                'y': random.randint(0, 1080),
                'timestamp': time.time()
            })
            
        # Keep only the last 100 movement records
        self.movement_data = self.movement_data[-100:]
        
        # Advanced metrics specific to gaming mice
        avg_click_distance = 0
        if len(self.movement_data) > 1:
            distances = []
            for i in range(1, len(self.movement_data)):
                prev = self.movement_data[i-1]
                curr = self.movement_data[i]
                distance = ((curr['x'] - prev['x'])**2 + (curr['y'] - prev['y'])**2)**0.5
                distances.append(distance)
            if distances:
                avg_click_distance = sum(distances) / len(distances)
        
        return {
            'device_id': self.device_id,
            'session_id': self.session_id,
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                'clicks_per_second': self.clicks_per_second,
                'movements_count': len(self.movement_data),
                'dpi': self.dpi,
                'polling_rate': self.polling_rate,
                'avg_click_distance': round(avg_click_distance, 2),
                'button_count': self.button_count
            },
            'status': {
                'under_attack': self.under_attack,
                'attack_duration': self._get_attack_duration() if self.under_attack else 0,
                'battery_level': random.randint(20, 100),  # Simulate battery level
                'connection_quality': random.randint(70, 100) if not self.under_attack else random.randint(30, 60)
            }
        }
        
    def _get_attack_duration(self):
        """Calculate attack duration in seconds"""
        if self.attack_start_time:
            return int(time.time() - self.attack_start_time)
        return 0
    
    def _publish_data(self, data):
        """Publish data via MQTT"""
        if not self.connected:
            return False
            
        try:
            payload = json.dumps(data)
            result = self.client.publish(self.data_topic, payload, qos=1)
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            print(f"Error publishing data: {e}")
            return False
    
    def _publish_status(self, status):
        """Publish device status via MQTT"""
        if not self.connected and status != "offline":
            return False
            
        try:
            payload = json.dumps({
                'device_id': self.device_id,
                'status': status,
                'timestamp': datetime.now().isoformat()
            })
            result = self.client.publish(self.status_topic, payload, qos=1, retain=True)
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            print(f"Error publishing status: {e}")
            return False
    
    def _publish_security_alert(self, alert_type, details):
        """Publish security alert via MQTT"""
        if not self.connected:
            return False
            
        try:
            payload = json.dumps({
                'device_id': self.device_id,
                'alert_type': alert_type,
                'timestamp': datetime.now().isoformat(),
                'details': details
            })
            result = self.client.publish(self.security_topic, payload, qos=2)  # Use QoS 2 for security alerts
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            print(f"Error publishing security alert: {e}")
            return False
    
    def _monitor_network(self):
        """Simulated network monitoring that doesn't rely on raw sockets"""
        while self.running:
            try:
                # Reset ping counter every second
                self.ping_count = 0
                
                # For simulation purposes, occasionally simulate an attack
                # 5% chance of simulated attack
                if random.random() < 0.05:
                    self.ping_count = random.randint(self.ping_threshold, self.ping_threshold + 50)
                else:
                    self.ping_count = random.randint(0, self.ping_threshold - 10)
                    
                # Sleep for a second to simulate the monitoring period
                time.sleep(1)
                
                # Check if we're under attack
                if self.ping_count > self.ping_threshold:
                    if not self.under_attack:
                        self.under_attack = True
                        self.attack_start_time = time.time()
                        print(f"⚠️ ALERT: Device is under attack! Received {self.ping_count} pings in 1 second")
                        
                        # Publish attack alert
                        self._publish_security_alert('attack_detected', {
                            'attack_type': 'ping_flood',
                            'intensity': self.ping_count,
                            'threshold': self.ping_threshold
                        })
                else:
                    if self.under_attack:
                        duration = self._get_attack_duration()
                        print(f"✓ Attack stopped. Duration: {duration} seconds")
                        
                        # Publish attack resolved alert
                        self._publish_security_alert('attack_resolved', {
                            'attack_type': 'ping_flood',
                            'duration': duration
                        })
                        
                        self.under_attack = False
                        self.attack_start_time = None
                
            except Exception as e:
                print(f"Error monitoring network: {e}")
                time.sleep(1)
    
    def _run(self):
        """Main execution loop"""
        while self.running:
            # Generate and publish performance data
            data = self._generate_performance_data()
            self._publish_data(data)
            
            # Sleep for the specified interval
            time.sleep(self.send_interval)

def main():
    parser = argparse.ArgumentParser(description='Simulated IoT Gaming Mouse with MQTT')
    parser.add_argument('--id', default='mouse-001', help='Device ID')
    parser.add_argument('--broker', default='localhost', help='MQTT broker address')
    parser.add_argument('--port', type=int, default=1883, help='MQTT broker port')
    parser.add_argument('--topic', default='iot/gaming/mouse', help='MQTT topic prefix')
    parser.add_argument('--interval', type=float, default=1.0, help='Data sending interval in seconds')
    args = parser.parse_args()
    
    try:
        mouse = SimulatedGamingMouse(
            device_id=args.id,
            mqtt_broker=args.broker,
            mqtt_port=args.port,
            mqtt_topic_prefix=args.topic,
            send_interval=args.interval
        )
        
        if mouse.start():
            # Keep the main thread running
            while True:
                try:
                    time.sleep(1)
                except KeyboardInterrupt:
                    print("Stopping simulation...")
                    mouse.stop()
                    break
        else:
            print("Failed to start the simulation")
                
    except Exception as e:
        print(f"Error: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    main()