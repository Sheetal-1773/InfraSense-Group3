---
title: 'Prometheus Remote Write Endpoint'
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

**Problem:** The platform needs to support Prometheus remote-write protocol so existing Prometheus exporters can push metrics without modification.

**Approach:** Add a Prometheus remote-write receiver to the OpenTelemetry Collector configuration that forwards metrics to the backend API.

## Boundaries & Constraints

**Always:**
- Support Prometheus remote-write on standard port 19291
- Data loss must be <1% under normal load
- Compatible with Prometheus remote-write format

**Ask First:**
- Whether to use OTel Collector Prometheus receiver or native endpoint

**Never:**
- Do not implement Prometheus scraping (only remote-write push)

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | Prometheus remote-write request | 200 OK, metrics stored | N/A |
| ERROR_INVALID_FORMAT | Malformed Prometheus payload | 400 Bad Request | Log and continue |

</frozen-after-approval>

## Code Map

- `otel-collector-config.yaml` -- Add Prometheus remote-write receiver
- `backend/app/routers/metrics.py` -- Extend to handle remote-write format

## Tasks & Acceptance

**Execution:**
- [x] `otel-collector-config.yaml` -- Add prometheus receiver for remote-write -- Enable Prometheus protocol
- [x] `backend/app/routers/metrics.py` -- Add remote-write format handler -- Support Prometheus format

**Acceptance Criteria:**
- Given a Prometheus remote-write endpoint is exposed, when Prometheus sends metrics via remote-write, then the metrics are accepted and stored in the database and data loss is <1% under normal load

## Spec Change Log

<!-- Append-only -->

## Design Notes

Use OTel Collector `prometheus` receiver with `remote_write` configuration:
```yaml
receivers:
  prometheus:
    config:
      remote_write:
        - url: http://localhost:19291/api/v1/write
```

## Verification

**Commands:**
- Check collector logs for Prometheus receiver starting

**Manual checks:**
- Verify port 19291 is listening