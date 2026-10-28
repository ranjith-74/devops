"""
Continuous Traffic Generator
----------------------------
Sends continuous HTTP requests to the Flask application:
  - Normal UI page requests ('/')
  - Automated API order creation ('/api/orders')
  - Heavy compute tasks ('/heavy')
"""

import os
import time
import random
import json
import urllib.request
import urllib.error

BASE_URL = os.getenv("TARGET_URL", "http://flask-app:5000").rstrip('/')
REQUEST_INTERVAL = float(os.getenv("REQUEST_INTERVAL", "0.35"))

print(f"[Traffic Generator] Starting traffic stream against: {BASE_URL}")
print(f"[Traffic Generator] Request Interval: {REQUEST_INTERVAL}s")

# Wait for Flask app to be healthy
while True:
    try:
        with urllib.request.urlopen(f"{BASE_URL}/", timeout=5) as response:
            if response.status == 200:
                print("[Traffic Generator] Connected to Flask app! Beginning traffic generation...")
                break
    except Exception as e:
        print(f"[Traffic Generator] Waiting for Flask app ({e}). Retrying in 2s...")
        time.sleep(2)

request_count = 0
PRODUCTS = ["PRD-001", "PRD-002", "PRD-003", "PRD-004", "PRD-005"]

while True:
    try:
        request_count += 1
        rand_choice = random.random()

        if rand_choice < 0.25:
            # 25% create a live order via POST /api/orders
            target = f"{BASE_URL}/api/orders"
            payload = json.dumps({
                "product_id": random.choice(PRODUCTS),
                "quantity": random.randint(1, 4)
            }).encode('utf-8')
            req = urllib.request.Request(target, data=payload, headers={'Content-Type': 'application/json'}, method='POST')
            with urllib.request.urlopen(req, timeout=5) as response:
                print(f"[Traffic] #{request_count:04d} -> POST /api/orders | Status: {response.status}")
        elif rand_choice < 0.35:
            # 10% hit /heavy
            target = f"{BASE_URL}/heavy"
            with urllib.request.urlopen(target, timeout=5) as response:
                print(f"[Traffic] #{request_count:04d} -> GET /heavy | Status: {response.status}")
        else:
            # 65% hit GET /
            target = f"{BASE_URL}/"
            with urllib.request.urlopen(target, timeout=5) as response:
                print(f"[Traffic] #{request_count:04d} -> GET / | Status: {response.status}")

    except urllib.error.HTTPError as e:
        print(f"[Traffic] #{request_count:04d} -> HTTP Error: {e.code}")
    except Exception as e:
        print(f"[Traffic] #{request_count:04d} -> Connection Error: {e}")

    time.sleep(REQUEST_INTERVAL)
