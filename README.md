# Monitoring Python Applications using Grafana and Prometheus on Docker

A production-grade, turnkey monitoring and observability stack featuring the **OrderFlow — Order Management System** web application, instrumented with Prometheus telemetry (CPU, Memory, Request Rates, Latency) and visualized on an auto-provisioned Grafana dashboard using Docker Compose.

---

## Architecture Overview

```text
               +-------------------------------------------------------------+
               |                       Docker Network                        |
               |                      (monitoring-net)                       |
               |                                                             |
+-----------+  |  +-------------------------------------------------------+  |
| Traffic   |---->|                      flask-app                        |  | (Port 5000)
| Generator |  |  |   - / (OrderFlow Web Interface)                       |  |
+-----------+  |  |   - /api/orders (POST order creation, GET list)       |  |
               |  |   - /api/health (System health & telemetry)           |  |
               |  |   - /api/simulate-error (Simulated HTTP 500)          |  |
               |  |   - /heavy (CPU prime calculation spike)              |  |
               |  |   - /metrics (Prometheus client + psutil)             |  |
               |  +-------------------------------------------------------+  |
               |                             ^                               |
               |                             | Scrapes every 5s              |
               |                             |                               |
               |  +-------------------------------------------------------+  |
               |  |                     prometheus                        |  | (Port 9090)
               |  |   - TSDB Engine & Scrape Scheduler                    |  |
               |  +-------------------------------------------------------+  |
               |                             ^                               |
               |                             | PromQL queries                |
               |                             |                               |
               |  +-------------------------------------------------------+  |
               |  |                      grafana                          |  | (Port 3000)
               |  |   - Auto-provisioned Datasource & Live Dashboard      |  |
               |  +-------------------------------------------------------+  |
               +-------------------------------------------------------------+
                                             |
                   Browser Web UI:   http://localhost:5000
                   Grafana Dashboard: http://localhost:3000
```

---

## Features & Endpoints

### 1. Interactive Web Interface: OrderFlow
Opening **[http://localhost:5000/](http://localhost:5000/)** renders a modern enterprise web interface built with pure HTML5, responsive CSS, and vanilla JavaScript (no React or heavy frameworks):
- **Live Status Badge**: Indicates application health and connectivity.
- **Product Selector & Quantity**: Choose items (Cloud Compute Nodes, Security Suites, Database Clusters) with dynamic live price calculation.
- **Create Order Button**: Sends `POST /api/orders`, executes a cryptographic SHA-256 verification loop (generating genuine CPU load), and records the transaction in memory.
- **View / Refresh Orders**: Sends `GET /api/orders` to dynamically reload the latest orders table.
- **Check Health Button**: Sends `GET /api/health` to fetch live CPU %, RAM (MB), and server uptime.
- **Simulate Error Button**: Sends `GET /api/simulate-error` to trigger an intentional HTTP 500 error for testing alerting and error rate metrics.
- **Trigger CPU Spike**: Sends `GET /heavy` to run prime factor calculations and drive CPU usage graphs in Grafana.
- **Real-Time Notification Toasts**: Floating feedback alerts for successes, warnings, and errors.

### 2. Telemetry & Metrics
| Metric | Type | Purpose |
| :--- | :--- | :--- |
| `flask_http_requests_total` | Counter | Total requests labelled by `endpoint` (`/`, `/api/orders`, `/api/health`, `/api/simulate-error`, `/heavy`) and `method` |
| `flask_http_request_duration_seconds` | Histogram | Request latency distributed into discrete buckets (`0.05s` to `1.0s`) |
| `flask_app_cpu_usage_percent` | Gauge | Live CPU % utilization of the Flask application process |
| `flask_app_memory_usage_megabytes` | Gauge | Resident Set Size (RSS) memory consumption in MB |
| `flask_app_active_records` | Gauge | Total in-memory transaction records currently cached |

---

## Quick Start & Rebuilding

To apply changes and rebuild the Docker stack:
```bash
docker compose up --build -d
```

### Accessing the Stack
| Service | URL | Description |
| :--- | :--- | :--- |
| **OrderFlow Web UI** | [http://localhost:5000](http://localhost:5000) | Interactive order management dashboard |
| **Grafana Dashboard** | [http://localhost:3000](http://localhost:3000) | Live metrics dashboard (Auto-login) |
| **Prometheus Targets**| [http://localhost:9090/targets](http://localhost:9090/targets) | Target health inspection (`UP`) |
| **Raw Metrics** | [http://localhost:5000/metrics](http://localhost:5000/metrics) | Plain-text Prometheus telemetry |

---

## Stopping the Containers

```bash
docker compose down
```
To stop and remove all volumes:
```bash
docker compose down -v
```
