import time
from collections import defaultdict
from scapy.all import sniff, IP, ICMP
import requests

SERVER_URL = "http://localhost:5000/api/security_log"
DEVICE_ID = "esport-mouse-01"
THRESHOLD_PINGS_PER_MIN = 30

ping_counts = defaultdict(int)

def process_packet(packet):
    if packet.haslayer(ICMP):
        src = packet[IP].src
        ping_counts[src] += 1

def send_attack_log(src, count):
    payload = {
        "device_id": DEVICE_ID,
        "event_type": "network_attack",
        "description": f"High ping rate from {src}: {count} pings/min",
        "severity": "critical",
        "timestamp": time.time()
    }
    try:
        resp = requests.post(SERVER_URL, json=payload, timeout=3)
        print("Attack logged:", payload)
    except Exception as e:
        print("Failed to log attack:", e)

def monitor_icmp():
    print("Monitoring for ICMP flood attacks...")
    while True:
        sniff(filter="icmp", prn=process_packet, timeout=60)
        for src, count in ping_counts.items():
            if count > THRESHOLD_PINGS_PER_MIN:
                print(f"ALERT: High ping rate from {src}: {count} pings/min")
                send_attack_log(src, count)
        ping_counts.clear()

if __name__ == "__main__":
    monitor_icmp()