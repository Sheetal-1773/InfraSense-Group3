---
title: 'Duration-Based Threshold Detection'
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

**Problem:** The platform needs to detect when a metric exceeds its threshold for a sustained duration to avoid false alerts from brief spikes.

**Approach:** Add duration tracking to the health service that tracks how long thresholds have been exceeded.

## Boundaries & Constraints

**Always:**
- Track duration when metric exceeds threshold
- Only trigger alert when duration threshold is met
- Reset timer when metric returns below threshold

**Ask First:**
- Default duration threshold value

**Never:**
- Do not trigger alerts for brief spikes

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| SPIKE | Exceeds for 2 min (threshold 5 min) | No alert | N/A |
| SUSTAINED | Exceeds for 5+ min | Alert with duration flag | N/A |
| RECOVERY | Returns below threshold | Timer reset | N/A |

</frozen-after-approval>

## Code Map

- `backend/app/services/health_service.py` -- Add duration tracking
- `backend/app/models/models.py` -- Add duration field to Threshold

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/models/models.py` -- Add duration_minutes to Threshold -- Duration config
- [x] `backend/app/services/health_service.py` -- Track threshold duration -- Sustained detection

**Acceptance Criteria:**
- Given a duration threshold is configured (e.g., CPU > 80% for 5 minutes), when the metric exceeds the threshold, then a timer starts tracking how long the threshold is exceeded
- Given a metric exceeds its threshold, when the duration threshold is NOT met (e.g., only 2 minutes), then no alert is generated
- Given a metric exceeds its threshold, when the duration threshold IS met (e.g., 5+ minutes), then an alert is generated with "duration" flag set and the alert includes the duration information
- Given a metric returns below threshold, when the duration timer is active, then the timer is reset

## Spec Change Log

<!-- Append-only -->

## Design Notes

Track duration in memory (per component/metric) and reset when metric returns below threshold.

## Verification

**Commands:**
- Test sustained exceedance -- expected: Alert after duration

**Manual checks:**
- Brief spike - no alert