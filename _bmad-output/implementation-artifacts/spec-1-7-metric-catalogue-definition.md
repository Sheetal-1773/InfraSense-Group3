---
title: 'Metric Catalogue Definition'
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

**Problem:** The platform needs a defined metric catalogue so it knows what metrics to collect and how to interpret them.

**Approach:** Create a metric catalogue with definitions for all supported component types (Server, Network, Application, Database).

## Boundaries & Constraints

**Always:**
- Support Server metrics: CPU, memory, disk, network
- Support Network metrics: bandwidth, packet loss, latency, error rate
- Support Application metrics: response time, request rate, error rate, connections
- Support Database metrics: query latency, connection pool, cache hit ratio, disk I/O

**Ask First:**
- None

**Never:**
- Do not hardcode thresholds in catalogue (use thresholds table)

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | Valid metric from catalogue | Accepted and stored | N/A |
| ERROR_UNKNOWN_METRIC | Unknown metric name | Logged as warning | N/A |

</frozen-after-approval>

## Code Map

- `backend/app/services/metric_catalogue.py` -- New service for metric definitions

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/services/metric_catalogue.py` -- Define metric catalogue -- All component types

**Acceptance Criteria:**
- Given the metric catalogue is defined, when the system starts, then it supports: Server (CPU, memory, disk, network), Network (bandwidth, packet loss, latency, error rate), Application (response time, request rate, error rate, connections), Database (query latency, connection pool, cache hit ratio, disk I/O)
- Given a metric is defined in the catalogue, when it is received from a component, then the metric is validated against its expected type and range and invalid metrics are logged with details

## Spec Change Log

<!-- Append-only -->

## Design Notes

Metric catalogue should be a data structure (dict) that can be extended. Each metric has: name, unit, type, description.

## Verification

**Commands:**
- Check metric catalogue loaded -- expected: All categories present

**Manual checks:**
- Validate metrics against catalogue