# InfraSense Real-Time Monitoring Environment

## Overview

This directory contains the complete real-time monitoring infrastructure for InfraSense using Docker Compose + Prometheus. The system replaces the previous Azure/AWS infrastructure dependency with a fully local, real-time monitoring environment.

## Architecture

```
Docker Host
├── customer-api (Prometheus metrics)
├── payment-api (Prometheus metrics)
├── auth-api (Prometheus metrics)
├── PostgreSQL + postgres_exporter
├── Prometheus (central metrics collector)
├── Node Exporter (server metrics: CPU, RAM, disk, network)
├── cAdvisor (Docker/container metrics)
├── postgres_exporter (database metrics)
└── blackbox-exporter (network/endpoint availability)
```

## Quick Start

### 1. Start the Monitoring Stack

```bash
# From the monitoring directory
cd monitoring
docker compose up -d
```

### 2. Verify Services Are Running

```bash
# Check all containers are running
docker ps

# Check Prometheus targets
curl http://localhost:9090/targets

# Check Prometheus metrics
curl http://localhost:9090/metrics
```

### 3. Access the Monitoring Dashboard

- **Prometheus Dashboard**: http://localhost:9090
- **Customer API**: http://localhost:3001
- **Payment API**: http://localhost:3002
- **Auth API**: http://localhost:3003
- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:3000

## Configuration Files

### `docker-compose.yml`

Main Docker Compose configuration file that defines all services, networks, and volumes.

### `prometheus.yml`

Prometheus configuration file that defines:
- Scrape intervals (15 seconds)
- Evaluation intervals (15 seconds)
- Scrape timeout (10 seconds)
- All monitoring targets
- Alert rules file

### `blackbox.yml`

Blackbox Exporter configuration for network monitoring including:
- HTTP 2xx checks
- TCP connection checks
- ICMP checks
- Network latency monitoring

### `alert.rules.yml`

Prometheus alert rules including:
- High CPU load alerts
- High memory usage alerts
- High disk usage alerts
- High network latency alerts
- High API error rate alerts
- High API latency alerts
- High database connection alerts
- High database query latency alerts

## Monitoring Components

### 1. Prometheus (Central Metrics Collector)

- **Port**: 9090
- **Purpose**: Central metrics collection and storage
- **Configuration**: `prometheus.yml`
- **Features**:
  - Real-time metrics collection at 15-second intervals
  - Time-series database storage
  - Alerting rules engine
  - Query language for metrics analysis

### 2. Node Exporter (Server Metrics)

- **Port**: 9100
- **Purpose**: Collect server-level metrics
- **Metrics Collected**:
  - CPU usage and frequency
  - Memory usage and availability
  - Disk usage and I/O
  - Network I/O and errors
  - System uptime
  - Process counts

### 3. cAdvisor (Container Metrics)

- **Port**: 8080
- **Purpose**: Collect Docker container metrics
- **Metrics Collected**:
  - Container CPU usage
  - Container memory usage
  - Container network I/O
  - Container disk I/O
  - Container process counts

### 4. PostgreSQL + postgres_exporter (Database Metrics)

- **PostgreSQL Port**: 5432
- **Exporter Port**: 9187
- **Purpose**: Collect database metrics
- **Metrics Collected**:
  - Database connections
  - Query execution times
  - Lock contention
  - Database size
  - Cache hit ratios
  - Replication lag

### 5. Blackbox Exporter (Network Monitoring)

- **Port**: 9115
- **Purpose**: Monitor network endpoints and availability
- **Metrics Collected**:
  - Endpoint availability (HTTP, TCP, ICMP)
  - Network latency
  - Packet loss
  - Connection timeouts
  - Service health checks

### 6. Application Services (API Metrics)

Each application service exposes Prometheus metrics at `/metrics` endpoint:

- **Customer API**: Port 9091
- **Payment API**: Port 9092
- **Auth API**: Port 9093
- **Backend API**: Port 9094
- **Frontend**: Port 9095

**Metrics Collected**:
- HTTP request duration
- HTTP request count
- HTTP error rates
- API response times
- API latency distributions
- API throughput
- API availability

## Backend Integration

The backend service connects to Prometheus and:

1. **Discover Components**: Automatically discovers all components from Prometheus
2. **Collect Metrics**: Pulls real-time metrics from Prometheus at 10-second intervals
3. **Calculate Health Scores**: Computes health scores based on real metrics
4. **Generate Alerts**: Creates alerts based on real metric thresholds
5. **Make Predictions**: Uses time-series data for predictive analytics
6. **Calculate Correlations**: Analyzes relationships between components

## Frontend Integration

The frontend displays:

1. **Real-time Health Scores**: Based on actual metrics
2. **Active Alerts**: Generated from real metric thresholds
3. **Predictions**: Based on time-series data
4. **Correlations**: Between actual components
5. **Component Details**: With real metric histories
6. **Dashboard Functionality**: All working with real data

## Troubleshooting

### Common Issues

1. **Prometheus not collecting metrics**
   - Check if all targets are UP in Prometheus dashboard
   - Verify network connectivity between containers
   - Check Prometheus logs: `docker logs prometheus`

2. **Services not starting**
   - Check container status: `docker ps -a`
   - Check logs: `docker logs <container_name>`
   - Verify dependencies are running

3. **Metrics not appearing**
   - Check if services are exposing `/metrics` endpoint
   - Verify Prometheus configuration includes all targets
   - Check if services are healthy: `docker inspect <container>`

4. **Database connection issues**
   - Check PostgreSQL health: `docker exec -it postgres pg_isready`
   - Verify credentials in environment variables
   - Check connection strings in application services

### Debugging Commands

```bash
# Check all running containers
docker ps

# Check container logs
docker logs <container_name>

# Check Prometheus targets
docker exec -it prometheus curl http://localhost:9090/targets

# Check Prometheus metrics
docker exec -it prometheus curl http://localhost:9090/metrics

# Check service health
curl http://localhost:3001/health
curl http://localhost:3002/health
curl http://localhost:3003/health
curl http://localhost:8000/api/health
```

## Verification Steps

### 1. Verify Docker Services Are Running

```bash
docker ps
```

Expected output should show all containers running:
- prometheus
- node-exporter
- cadvisor
- postgres
- postgres-exporter
- blackbox-exporter
- customer-api
- payment-api
- auth-api
- backend
- frontend

### 2. Verify Exporters Are Producing Metrics

```bash
# Check Node Exporter
curl http://localhost:9100/metrics

# Check cAdvisor
curl http://localhost:8080/metrics

# Check PostgreSQL Exporter
curl http://localhost:9187/metrics

# Check Blackbox Exporter
curl http://localhost:9115/metrics

# Check Application Services
curl http://localhost:3001/metrics
curl http://localhost:3002/metrics
curl http://localhost:3003/metrics
```

### 3. Verify Prometheus Targets Are UP

```bash
curl http://localhost:9090/targets
```

Expected output should show all targets as UP with green status.

### 4. Verify Backend Is Receiving Real Metrics

```bash
curl http://localhost:8000/api/components
curl http://localhost:8000/api/alerts
curl http://localhost:8000/api/predictions
curl http://localhost:8000/api/correlations
```

### 5. Verify Database Is Storing/Updating Metrics

```bash
# Connect to PostgreSQL
psql -h localhost -U infrasense -d infrasense

# Check metrics tables
SELECT * FROM metrics;
SELECT * FROM component_metrics;
SELECT * FROM alert_history;
```

### 6. Verify Alerts Are Generated

```bash
curl http://localhost:8000/api/alerts?status=active
```

### 7. Verify Health Scores Are Changing

```bash
curl http://localhost:8000/api/components/health
```

### 8. Verify Predictions Are Updating

```bash
curl http://localhost:8000/api/predictions
```

### 9. Verify Correlations Are Updating

```bash
curl http://localhost:8000/api/correlations
```

### 10. Verify Frontend Is Displaying Live Data

Open browser to: http://localhost:3000

Verify all components show real metrics and health scores update in real-time.

## Performance Optimization

### Prometheus Configuration

- **Scrape Interval**: 15 seconds (adjustable in `prometheus.yml`)
- **Evaluation Interval**: 15 seconds (adjustable in `prometheus.yml`)
- **Scrape Timeout**: 10 seconds (adjustable in `prometheus.yml`)

### Database Optimization

- **TimescaleDB**: Used for time-series data optimization
- **Connection Pooling**: Configured in PostgreSQL
- **Indexing**: Automatic indexing for time-series data

### Application Optimization

- **Metrics Collection**: All services expose `/metrics` endpoint
- **Health Checks**: All services have health check endpoints
- **Error Handling**: Comprehensive error handling in all services
- **Logging**: Structured logging in all services

## Scaling

### Horizontal Scaling

To scale the monitoring infrastructure:

1. **Add more application instances**
2. **Add more database replicas**
3. **Add more monitoring nodes**
4. **Distribute load across multiple hosts**

### Vertical Scaling

To scale individual components:

1. **Increase resource allocation**
2. **Optimize database queries**
3. **Optimize application code**
4. **Optimize monitoring queries**

## Monitoring Best Practices

1. **Set up proper alerts**
2. **Monitor key metrics**
3. **Set up proper dashboards**
4. **Set up proper notifications**
5. **Set up proper escalation paths**
6. **Set up proper documentation**
7. **Set up proper training**
8. **Set up proper support**

## Support

For issues or questions, please contact the InfraSense support team.

## License

This monitoring infrastructure is licensed under the MIT License.

## Conclusion

This monitoring infrastructure provides a complete real-time monitoring solution for InfraSense. All components are running locally through Docker Compose, and Prometheus is collecting real metrics at short intervals. The backend is connected to Prometheus and exposing real metrics through the existing APIs. All dashboard components are clickable and show real metric details and history.

The entire environment can be started with one command: `docker compose up -d`