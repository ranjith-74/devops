"""
Local Traffic Generator Script
------------------------------
Run this on your host machine to generate extra traffic or test the app directly.
Simulates real users placing orders and triggers occasional heavy compute tasks.
Usage:
    python generate_traffic.py
"""

import os
import time
import random
import urllib.request
import urllib.error

BASE_URL = os.getenv("TARGET_URL", "http://localhost:5000").rstrip('/')
REQUEST_INTERVAL = float(os.getenv("REQUEST_INTERVAL", "0.2"))

print("=" * 65)
print(" Local Order Processing Traffic Simulator")
print(f" Target URL: {BASE_URL}")
print(f" Request Interval: {REQUEST_INTERVAL}s")
print(" Sending continuous orders (85% '/') and compute tasks (15% '/heavy')")
print(" Press Ctrl+C to stop")
print("=" * 65)

req_id = 0
try:
    while True:
        req_id += 1
        route = "/heavy" if (random.random() < 0.15) else "/"
        target = f"{BASE_URL}{route}"
        t0 = time.time()
        try:
            with urllib.request.urlopen(target, timeout=5) as resp:
                duration = time.time() - t0
                print(f"[Request #{req_id:04d}] GET {route:<6} | Status: {resp.status} | Time: {duration:.3f}s")
        except urllib.error.URLError as err:
            print(f"[Request #{req_id:04d}] Error connecting to {target}: {err.reason}")
        time.sleep(REQUEST_INTERVAL)
except KeyboardInterrupt:
    print(f"\nStopped traffic generator after {req_id} requests.")
