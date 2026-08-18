---
title: 'OpenTelemetry Collector Setup'
type: 'feature'
created: '2026-08-12'
status: 'complete'
updated: '2026-08-18'
review_loop_iteration: 0
context: []
baseline_commit: 'NO_VCS'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The platform needs to collect infrastructure metrics reliably from various sources (servers, databases, networks, applications) via OpenTelemetry protocol.

**Approach:** Deploy an OpenTelemetry Collector with OTLP receivers (gRPC on port 4317, HTTP on port 4318) that accepts metrics and forwards them to the backend API for storage.

## Boundaries & Constraints

**Always:**
- Collector must support both OTLP/gRPC (4317) and OTLP/HTTP (4318)
- Data loss must be <1% under normal load
- Collector must have health check endpoint
- Docker Compose setup for local development

**Ask First:**
- Which OTel Collector distribution to use (core vs contrib)
- Whether to include any additional receivers (e.g., Prometheus)

**Never:**
- Do not implement metric processing/aggregation in collector (keep it simple pass-through)
- Do not implement storage backend in collector (use backend API)

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH_1 | OTLP/gRPC request on 4317 with valid metrics | 200 OK, metrics forwarded to backend | N/A |
| HAPPY_PATH_2 | OTLP/HTTP request on 4318 with valid metrics | 200 OK, metrics forwarded to backend | N/A |
| ERROR_INVALID_FORMAT | Malformed OTLP payload | 400 Bad Request, error logged | Log and continue |
| ERROR_BACKEND_DOWN | Backend API unreachable | Retry with exponential backoff, queue in memory | 5 retries, then drop with warning |

</frozen-after-approval>

## Code Map

- `docker-compose.yml` -- OTel Collector service definition
- `otel-collector-config.yaml` -- Collector configuration (receivers, exporters)
- `backend/app.py` -- FastAPI backend to receive metrics from collector
- `backend/models.py` -- Pydantic models for metric data

## Tasks & Acceptance

**Execution:**
- [x] `docker-compose.yml` -- Add OTel Collector service with OTLP receivers -- Container orchestration
- [x] `otel-collector-config.yaml` -- Configure OTLP receivers (gRPC 4317, HTTP 4318) and exporter -- Collector configuration
- [x] `backend/app/routers/metrics.py` -- Add POST /api/v1/metrics endpoint to receive metrics from collector -- Backend API
- [x] `backend/app/main.py` -- Register metrics router -- Router registration

**Acceptance Criteria:**
- Given a running OpenTelemetry Collector instance, when metrics are sent via OTLP/gRPC on port 4317, then the collector accepts and processes the metrics and metrics are stored in the database with <1% data loss
- Given a running OpenTelemetry Collector instance, when metrics are sent via OTLP/HTTP on port 4318, then the collector accepts and processes the metrics and metrics are stored in the database with <1% data loss

## Spec Change Log

<!-- Append-only. Populated by step-04 during review loops. -->

## Design Notes

**Distribution:** Use `otelcol-contrib` for broader receiver/exporter support.

**Configuration Structure:**
```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

exporters:
  otlp:
    endpoint: backend:8000
    tls:
      insecure: true

service:
  pipelines:
    metrics:
      receivers: [otlp]
      exporters: [otlp]
```

## Verification

**Commands:**
- `docker-compose up -d` -- expected: Collector starts without errors
- `curl http://localhost:13133` -- expected: Health check returns 200
- `grpcurl -d @ localhost:4317 list` -- expected: OTLP service listed

**Manual checks (if no CLI):**
- Check collector logs for "Starting" message
- Verify ports 4317 and 4318 are listening