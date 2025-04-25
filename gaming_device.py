import socket
import time
import json
import random
import threading
from datetime import datetime

class GamingPeripheral:
    def __init__(self, device_type="keyboard", port=5555):
        self.device_type = device_type
        self.port = port
        self.running = True
        self.metrics = {
            'input_rate': 0,
            'response_time': 0,
            'error_rate': 0,
            'battery_level': 100,
            'connection_quality': 100
        }
        
    def start(self):
        """Start the IoT device simulation"""
        # Start UDP server to receive commands
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', self.port))
        print(f"IoT {self.device_type} simulator running on port {self.port}")
        
        # Start metrics generation thread
        self.metrics_thread = threading.Thread(target=self._generate_metrics)
        self.metrics_thread.daemon = True
        self.metrics_thread.start()
        
        # Listen for incoming packets
        while self.running:
            try:
                data, addr = self.sock.recvfrom(1024)
                if data:
                    # Check if under attack based on packet frequency
                    self._check_attack(addr[0])
            except Exception as e:
                print(f"Error receiving data: {e}")
                
    def _generate_metrics(self):
        """Generate simulated device metrics"""
        while self.running:
            # Simulate normal device operation
            self.metrics['input_rate'] = random.randint(60, 200)
            self.metrics['response_time'] = random.uniform(1, 5)
            self.metrics['error_rate'] = random.uniform(0, 0.5)
            self.metrics['battery_level'] = max(0, self.metrics['battery_level'] - random.uniform(0, 0.1))
            self.metrics['connection_quality'] = max(0, min(100, self.metrics['connection_quality'] + random.uniform(-1, 1)))
            
            # Send metrics to monitoring server
            self._send_metrics()
            time.sleep(1)
            
    def _check_attack(self, source_ip):
        """Check if device is under attack based on packet frequency"""
        # Track packet frequency
        current_time = time.time()
        if not hasattr(self, '_last_check_time'):
            self._last_check_time = current_time
            self._packet_count = 0
        
        self._packet_count += 1
        
        # Check rate every second
        if current_time - self._last_check_time >= 1:
            if self._packet_count > 100:  # Threshold for attack detection
                self._report_attack(source_ip, self._packet_count)
            self._packet_count = 0
            self._last_check_time = current_time
            
    def _report_attack(self, source_ip, packet_count):
        """Report attack to monitoring server"""
        try:
            attack_data = {
                'device_type': self.device_type,
                'port': self.port,
                'attack_source': source_ip,
                'packet_count': packet_count,
                'timestamp': datetime.now().isoformat()
            }
            # Send attack data to monitoring server
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('localhost', 5000))
            sock.send(json.dumps(attack_data).encode())
            sock.close()
        except Exception as e:
            print(f"Error reporting attack: {e}")
            
    def _send_metrics(self):
        """Send device metrics to monitoring server"""
        try:
            metrics_data = {
                'device_type': self.device_type,
                'metrics': self.metrics,
                'timestamp': datetime.now().isoformat()
            }
            # Send metrics to monitoring server
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('localhost', 5000))
            sock.send(json.dumps(metrics_data).encode())
            sock.close()
        except Exception as e:
            print(f"Error sending metrics: {e}")

def main():
    # Create simulated devices
    devices = [
        GamingPeripheral("keyboard", 5555),
        GamingPeripheral("mouse", 5556),
        GamingPeripheral("headset", 5557)
    ]
    
    # Start device threads
    threads = []
    for device in devices:
        thread = threading.Thread(target=device.start)
        thread.daemon = True
        thread.start()
        threads.append(thread)
        
    # Wait for threads
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down simulators...")
        for device in devices:
            device.running = False

if __name__ == "__main__":
    main()
