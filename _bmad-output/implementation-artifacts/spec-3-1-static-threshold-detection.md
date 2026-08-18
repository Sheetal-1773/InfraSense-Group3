---
title: 'Static Threshold Detection'
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

**Problem:** The platform needs to detect when metrics exceed configured static thresholds.

**Approach:** Create anomaly detection service that checks metrics against static thresholds and records anomalies.

## Boundaries & Constraints

**Always:**
- Check metrics against configured thresholds
- Record anomaly with metric name, value, threshold, timestamp
- No anomaly if within thresholds

**Ask First:**
- None

**Never:**
- Do not trigger alerts (that's story 3-2)

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| EXCEEDS | Metric > threshold | Anomaly recorded | N/A |
| WITHIN | Metric < threshold | No anomaly | N/A |

</frozen-after-approval>

## Code Map

- `backend/app/services/anomaly_service.py` -- Create new service

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/services/anomaly_service.py` -- Create anomaly detection -- Static threshold check

**Acceptance Criteria:**
- Given static thresholds are configured for a component, when a metric value exceeds the threshold, then an anomaly is recorded in the database and the anomaly includes the metric name, value, threshold, and timestamp
- Given static thresholds are configured, when a metric is within thresholds, then no anomaly is recorded

## Spec Change Log

<!-- Append-only -->

## Design Notes

Create new anomaly_service.py with static threshold detection logic.

## Verification

**Commands:**
- Test threshold exceedance -- expected: Anomaly recorded

**Manual checks:**
- Within threshold - no anomaly