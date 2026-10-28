"""
OrderFlow — Order Management Microservice with Prometheus Monitoring
--------------------------------------------------------------------
A realistic Python microservice featuring:
  - Interactive HTML/CSS/JS frontend (OrderFlow UI)
  - Full REST API endpoints for order creation, order viewing, health checks, and error simulations
  - Cryptographic SHA-256 verification (real CPU work)
  - Stateful in-memory transaction cache (real RAM consumption)
  - Downstream simulation latency (50ms - 400ms)
  - Prometheus metrics instrumentation via prometheus_client and psutil

Prometheus Metrics:
  - flask_http_requests_total: Counter tracking HTTP requests by endpoint & method
  - flask_http_request_duration_seconds: Histogram tracking request duration in seconds
  - flask_app_cpu_usage_percent: Gauge tracking live process CPU percentage
  - flask_app_memory_usage_megabytes: Gauge tracking live process Resident Set Size (RSS) in MB
  - flask_app_active_records: Gauge tracking total orders currently held in the in-memory cache
"""

import os
import time
import random
import hashlib
import uuid
import datetime
import psutil
from flask import Flask, Response, jsonify, render_template, request
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# Initialize Flask application
app = Flask(__name__)
APP_START_TIME = time.time()

# Track current OS process for CPU and memory usage
current_process = psutil.Process(os.getpid())
current_process.cpu_percent(interval=None)  # Prime cpu_percent

# Standard Product Catalog
PRODUCTS = {
    "PRD-001": {"name": "Cloud Compute Node 8-vCPU", "price": 120.00},
    "PRD-002": {"name": "Enterprise Security Suite", "price": 450.00},
    "PRD-003": {"name": "Managed PostgreSQL Cluster", "price": 280.00},
    "PRD-004": {"name": "Developer Workstation Pro", "price": 1899.00},
    "PRD-005": {"name": "AI Inference Accelerator", "price": 750.00}
}

# In-memory transaction cache (pre-seeded with initial records)
MAX_CACHE_SIZE = 5000
TRANSACTION_CACHE = [
    {
        "order_id": "ORD-A109F2B4",
        "product": "Cloud Compute Node 8-vCPU",
        "quantity": 2,
        "unit_price": 120.0,
        "amount_usd": 240.0,
        "status": "Completed",
        "signature": "7f8b91a24c5e6d80",
        "latency_seconds": 0.124,
        "timestamp": time.time() - 90,
        "created_at": (datetime.datetime.now() - datetime.timedelta(minutes=2)).strftime("%H:%M:%S")
    },
    {
        "order_id": "ORD-C88219E0",
        "product": "Enterprise Security Suite",
        "quantity": 1,
        "unit_price": 450.0,
        "amount_usd": 450.0,
        "status": "Completed",
        "signature": "3e4d5f6a7b8c9d0e",
        "latency_seconds": 0.189,
        "timestamp": time.time() - 30,
        "created_at": (datetime.datetime.now() - datetime.timedelta(minutes=1)).strftime("%H:%M:%S")
    }
]

# ---------------------------------------------------------
# Prometheus Metrics Definitions
# ---------------------------------------------------------

REQUEST_COUNT = Counter(
    name='flask_http_requests_total',
    documentation='Total count of HTTP requests received by the Flask application',
    labelnames=['endpoint', 'method']
)

REQUEST_LATENCY = Histogram(
    name='flask_http_request_duration_seconds',
    documentation='HTTP request latency in seconds for the Flask application',
    labelnames=['endpoint', 'method'],
    buckets=[0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.75, 1.0]
)

CPU_USAGE_GAUGE = Gauge(
    name='flask_app_cpu_usage_percent',
    documentation='Current CPU usage percentage of the Flask application process'
)

MEMORY_USAGE_GAUGE = Gauge(
    name='flask_app_memory_usage_megabytes',
    documentation='Current Resident Set Size (RSS) memory of the Flask process in MB'
)

ACTIVE_RECORDS_GAUGE = Gauge(
    name='flask_app_active_records',
    documentation='Total transaction records stored in memory'
)


def update_resource_metrics():
    """Reads live CPU and memory utilization from the OS process."""
    try:
        cpu_pct = current_process.cpu_percent(interval=None)
        CPU_USAGE_GAUGE.set(cpu_pct)

        mem_info = current_process.memory_info()
        mem_mb = mem_info.rss / (1024 * 1024)
        MEMORY_USAGE_GAUGE.set(mem_mb)

        ACTIVE_RECORDS_GAUGE.set(len(TRANSACTION_CACHE))
    except Exception:
        pass


# ---------------------------------------------------------
# Application Routes
# ---------------------------------------------------------

@app.route('/')
def home():
    """
    Main Route:
    - If accessed by a web browser, renders the interactive OrderFlow web UI.
    - If accessed by automated clients requesting application/json, processes a synthetic order.
    """
    start_time = time.time()

    # Support JSON requests for headless background generators/API clients
    if request.headers.get('Accept') == 'application/json' or request.args.get('format') == 'json':
        # Generate synthetic order
        order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        num_items = random.randint(1, 4)
        prod = random.choice(list(PRODUCTS.values()))
        total_amount = round(prod["price"] * num_items, 2)

        # Real CPU computation (SHA-256 hashing)
        raw_payload = f"{order_id}:{num_items}:{total_amount}:{time.time()}"
        digest = raw_payload
        for _ in range(4000):
            digest = hashlib.sha256(digest.encode('utf-8')).hexdigest()

        # Simulated I/O latency (50ms - 300ms)
        io_delay = random.uniform(0.05, 0.30)
        time.sleep(io_delay)

        transaction = {
            "order_id": order_id,
            "product": prod["name"],
            "quantity": num_items,
            "unit_price": prod["price"],
            "amount_usd": total_amount,
            "status": "Completed",
            "signature": digest[:16],
            "latency_seconds": round(time.time() - start_time, 4),
            "timestamp": time.time(),
            "created_at": datetime.datetime.now().strftime("%H:%M:%S")
        }
        TRANSACTION_CACHE.append(transaction)
        if len(TRANSACTION_CACHE) > MAX_CACHE_SIZE:
            TRANSACTION_CACHE.pop(0)

        duration = time.time() - start_time
        REQUEST_COUNT.labels(endpoint='/', method='GET').inc()
        REQUEST_LATENCY.labels(endpoint='/', method='GET').observe(duration)
        update_resource_metrics()

        return jsonify({
            "status": "success",
            "order": transaction,
            "latency_seconds": round(duration, 4)
        }), 200

    # Default for browser users: Serve the interactive OrderFlow HTML UI
    duration = time.time() - start_time
    REQUEST_COUNT.labels(endpoint='/', method='GET').inc()
    REQUEST_LATENCY.labels(endpoint='/', method='GET').observe(duration)
    update_resource_metrics()

    return render_template('index.html', products=PRODUCTS)


@app.route('/api/orders', methods=['POST'])
def create_order():
    """
    API Route: Create a new customer order.
    Receives product and quantity from the web UI, performs cryptographic verification,
    and saves to in-memory transaction registry.
    """
    start_time = time.time()
    data = request.get_json() or {}

    product_id = data.get('product_id', 'PRD-001')
    product_info = PRODUCTS.get(product_id, {"name": data.get('product', 'Custom Service'), "price": 100.00})
    quantity = int(data.get('quantity', 1))
    unit_price = product_info["price"]
    total_amount = round(unit_price * quantity, 2)

    order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"

    # Real CPU Work: Cryptographic SHA-256 signature verification loop
    raw_payload = f"{order_id}:{product_info['name']}:{quantity}:{total_amount}:{time.time()}"
    digest = raw_payload
    for _ in range(5000):
        digest = hashlib.sha256(digest.encode('utf-8')).hexdigest()

    # Real I/O Latency simulation (60ms - 250ms)
    io_delay = random.uniform(0.06, 0.25)
    time.sleep(io_delay)

    duration = time.time() - start_time

    # Record in transaction cache
    order_record = {
        "order_id": order_id,
        "product": product_info["name"],
        "quantity": quantity,
        "unit_price": unit_price,
        "amount_usd": total_amount,
        "status": "Completed",
        "signature": digest[:16],
        "latency_seconds": round(duration, 4),
        "timestamp": time.time(),
        "created_at": datetime.datetime.now().strftime("%H:%M:%S")
    }
    TRANSACTION_CACHE.append(order_record)
    if len(TRANSACTION_CACHE) > MAX_CACHE_SIZE:
        TRANSACTION_CACHE.pop(0)

    # Record metrics
    REQUEST_COUNT.labels(endpoint='/api/orders', method='POST').inc()
    REQUEST_LATENCY.labels(endpoint='/api/orders', method='POST').observe(duration)
    update_resource_metrics()

    cpu_val = current_process.cpu_percent(interval=None)
    mem_mb_val = round(current_process.memory_info().rss / (1024 * 1024), 2)

    return jsonify({
        "status": "success",
        "message": "Order created and processed successfully",
        "order": order_record,
        "performance": {
            "latency_seconds": round(duration, 4)
        },
        "process_resources": {
            "cpu_usage_percent": cpu_val,
            "memory_usage_mb": mem_mb_val,
            "active_cached_records": len(TRANSACTION_CACHE)
        }
    }), 201


@app.route('/api/orders', methods=['GET'])
def get_orders():
    """
    API Route: Fetch the list of recent orders from memory.
    """
    start_time = time.time()

    recent_orders = list(reversed(TRANSACTION_CACHE[-50:]))
    duration = time.time() - start_time

    REQUEST_COUNT.labels(endpoint='/api/orders', method='GET').inc()
    REQUEST_LATENCY.labels(endpoint='/api/orders', method='GET').observe(duration)
    update_resource_metrics()

    return jsonify({
        "status": "success",
        "count": len(TRANSACTION_CACHE),
        "orders": recent_orders
    }), 200


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    API Route: Application health check and resource telemetry report.
    """
    start_time = time.time()

    cpu_val = current_process.cpu_percent(interval=None)
    mem_mb_val = round(current_process.memory_info().rss / (1024 * 1024), 2)
    uptime = round(time.time() - APP_START_TIME, 1)

    duration = time.time() - start_time

    REQUEST_COUNT.labels(endpoint='/api/health', method='GET').inc()
    REQUEST_LATENCY.labels(endpoint='/api/health', method='GET').observe(duration)
    update_resource_metrics()

    return jsonify({
        "status": "healthy",
        "service": "OrderFlow Application",
        "uptime_seconds": uptime,
        "resources": {
            "cpu_usage_percent": cpu_val,
            "memory_usage_mb": mem_mb_val,
            "active_cached_orders": len(TRANSACTION_CACHE)
        }
    }), 200


@app.route('/api/simulate-error', methods=['GET'])
def simulate_error():
    """
    API Route: Generates an intentional HTTP 500 Internal Server Error.
    Useful for testing Grafana alerting and HTTP error monitoring panels.
    """
    start_time = time.time()
    time.sleep(0.05)
    duration = time.time() - start_time

    REQUEST_COUNT.labels(endpoint='/api/simulate-error', method='GET').inc()
    REQUEST_LATENCY.labels(endpoint='/api/simulate-error', method='GET').observe(duration)
    update_resource_metrics()

    return jsonify({
        "status": "error",
        "error_code": "INTERNAL_SERVER_ERROR",
        "message": "Simulated 500 error triggered for monitoring and alerting test"
    }), 500


@app.route('/heavy')
def heavy_computation():
    """
    Stress route: Computes prime factor calculations to produce deliberate CPU spikes.
    """
    start_time = time.time()

    n = 99999999
    primes = []
    d = 2
    temp = n
    while d * d <= temp:
        while (temp % d) == 0:
            primes.append(d)
            temp //= d
        d += 1
    if temp > 1:
        primes.append(temp)

    time.sleep(0.1)
    duration = time.time() - start_time

    REQUEST_COUNT.labels(endpoint='/heavy', method='GET').inc()
    REQUEST_LATENCY.labels(endpoint='/heavy', method='GET').observe(duration)
    update_resource_metrics()

    return jsonify({
        "status": "completed",
        "action": "Heavy Prime Calculation",
        "primes": primes,
        "duration_seconds": round(duration, 4)
    }), 200


@app.route('/metrics')
def metrics():
    """
    Prometheus metrics route:
    Outputs standard Prometheus metrics scraped by Prometheus server.
    Note: Does NOT increment REQUEST_COUNT to avoid polluting app traffic counts.
    """
    update_resource_metrics()
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


# ---------------------------------------------------------
# Entry Point
# ---------------------------------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
