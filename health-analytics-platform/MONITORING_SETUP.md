# Monitoring Setup Guide

## Overview

This guide explains how to set up and run the monitoring infrastructure for InfraSense using Docker Compose + Prometheus.

---

## Quick Start

```bash
cd health-analytics-platform
docker-compose up -d
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MONITORING STACK                          │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Prometheus  │  │   Node      │  │   cAdvisor  │         │
│  │   :9090     │  │  Exporter   │  │             │         │
│  │             │  │   :9100     │  │   :8080     │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ PostgreSQL  │  │  Blackbox   │  │ Application │         │
│  │   :5432     │  │  Exporter   │  │   Services  │         │
│  │             │  │   :9115     │  │             │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. Prometheus (Port 9090)
- Central metrics collector
- 15-second scrape intervals
- Time-series database
- Alert rules engine

### 2. Node Exporter (Port 9100)
- CPU usage and frequency
- Memory usage and availability
- Disk usage and I/O
- Network I/O and errors

### 3. cAdvisor (Port 8080)
- Container CPU usage
- Container memory usage
- Container network I/O
- Container disk I/O

### 4. PostgreSQL (Port 5432)
- Main database
- TimescaleDB for time-series
- Metrics storage

### 5. Blackbox Exporter (Port 9115)
- HTTP endpoint monitoring
- TCP connection checks
- Network latency monitoring

---

## Configuration Files

| File | Purpose |
|------|---------|
| `docker-compose.yml` | All services orchestration |
| `monitoring/prometheus.yml` | Prometheus scrape config |
| `monitoring/blackbox.yml` | Blackbox monitoring config |
| `monitoring/alert.rules.yml` | Alert definitions |

---

## Verification

### Check Running Containers
```bash
docker ps
```

### Check Prometheus Targets
```bash
curl http://localhost:9090/targets
```

### Check Metrics
```bash
curl http://localhost:9090/metrics
```

### Check Node Exporter
```bash
curl http://localhost:9100/metrics
```

---

## Access Points

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Prometheus | http://localhost:9090 |
| API Docs | http://localhost:8000/docs |

---

## Troubleshooting

### Prometheus not collecting
```bash
# Check targets
curl http://localhost:9090/targets

# Check logs
docker logs prometheus
```

### Services not starting
```bash
# Check all containers
docker ps -a

# Check specific service
docker logs <container_name>
```

### Database connection issues
```bash
# Check PostgreSQL
docker exec -it postgres pg_isready -U infrasense
```

---

## Next Steps

After monitoring is running:
1. Start backend: `cd backend && uvicorn app.main:app --reload`
2. Start frontend: `npm run dev`
3. Open http://localhost:5173

See [README.md](README.md) for full documentation.