---
title: 'Metrics Storage Schema'
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

**Problem:** The platform needs an efficient database schema to store raw metrics for health scoring and prediction.

**Approach:** Enhance the existing ComponentMetric table to include labels field and optimize indexes for time-series queries.

## Boundaries & Constraints

**Always:**
- Store component_id, metric_name, value, timestamp, labels
- Queries for last 24 hours complete in <1 second for 1000 components
- Support 10,000 metrics/second with <1% data loss

**Ask First:**
- None

**Never:**
- Do not change existing API contracts

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | Write metric with labels | Metric stored with all fields | N/A |
| HAPPY_PATH | Query last 24 hours | Results in <1 second | N/A |
| HIGH_LOAD | 10k metrics/second | <1% data loss, <100ms latency | Retry with backoff |

</frozen-after-approval>

## Code Map

- `backend/app/models/models.py` -- ComponentMetric model with labels field
- `backend/app/routers/metrics.py` -- Store metrics in database

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/models/models.py` -- Add labels JSON column to ComponentMetric -- Store metric labels
- [x] `backend/app/routers/metrics.py` -- Store metrics in database -- Persist metrics

**Acceptance Criteria:**
- Given PostgreSQL database is available, when the metrics table schema is created, then it stores: component_id, metric_name, value, timestamp, labels and queries for the last 24 hours complete in <1 second for 1000 components
- Given the metrics table exists, when 10,000 metrics per second are written, then data loss is <1% and write latency remains under 100ms

## Spec Change Log

<!-- Append-only -->

## Design Notes

Add JSON column for labels to support OpenTelemetry resource attributes and metric labels.

## Verification

**Commands:**
- Write 1000 metrics and query -- expected: <1 second

**Manual checks:**
- Check database indexes exist