---
title: 'Health Score Calculation Engine'
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

**Problem:** The platform needs a health score calculation engine that computes 0-100 scores for each component based on metrics.

**Approach:** The existing HealthCalculator class already implements this. This story verifies and enhances it.

## Boundaries & Constraints

**Always:**
- Score range: 0-100
- Based on CPU, memory, disk, network metrics
- Runs every 60 seconds

**Ask First:**
- None

**Never:**
- Do not break existing calculation logic

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| CRITICAL | CPU at 95% | Score 0-30 (Critical) | N/A |
| WARNING | CPU at 50% | Score 31-70 (Warning) | N/A |
| HEALTHY | CPU at 20% | Score 71-100 (Healthy) | N/A |

</frozen-after-approval>

## Code Map

- `backend/app/services/health_service.py` -- HealthCalculator class (already exists)

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/services/health_service.py` -- Verify HealthCalculator -- Already implemented

**Acceptance Criteria:**
- Given component metrics are stored in the database, when the health score calculation runs (every 60 seconds), then each component receives a score between 0-100 and the score is based on CPU, memory, disk, and network metrics
- Given a component with CPU at 95%, when the health score is calculated, then the score should be in the critical range (0-30)
- Given a component with CPU at 50%, when the health score is calculated, then the score should be in the warning range (31-70)
- Given a component with CPU at 20%, when the health score is calculated, then the score should be in the healthy range (71-100)

## Spec Change Log

<!-- Append-only -->

## Design Notes

The HealthCalculator class is already implemented in health_service.py with:
- DEFAULT_THRESHOLDS for various metric types
- calculate_health_score() method
- _calculate_metric_score() for individual metrics
- get_status() for status classification

## Verification

**Commands:**
- Run health calculation -- expected: Scores 0-100

**Manual checks:**
- Verify score ranges match AC