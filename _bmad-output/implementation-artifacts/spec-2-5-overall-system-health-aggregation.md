---
title: 'Overall System Health Aggregation'
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

**Problem:** The platform needs to calculate overall system health using weighted aggregation based on component criticality.

**Approach:** Enhance calculate_overall_health to use criticality-based weighting and cap at lowest critical component.

## Boundaries & Constraints

**Always:**
- Weighted aggregation based on component criticality
- Critical components have 2x weight
- If any component is critical, cap overall at lowest critical score

**Ask First:**
- None

**Never:**
- Do not break existing health calculation

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | All healthy | Weighted average | N/A |
| CRITICAL_PRESENT | Any critical component | Capped at lowest critical | N/A |

</frozen-after-approval>

## Code Map

- `backend/app/services/health_service.py` -- Enhance calculate_overall_health

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/services/health_service.py` -- Add criticality weighting -- Weighted aggregation

**Acceptance Criteria:**
- Given component health scores exist, when overall system health is calculated, then it uses weighted aggregation based on component criticality and critical components have 2x weight compared to non-critical
- Given overall system health is calculated, when any component is in critical state (score 0-30), then overall health is capped at the lowest critical component score
- Given overall system health is displayed, when a user views the dashboard, then they see a single health score for the entire infrastructure

## Spec Change Log

<!-- Append-only -->

## Design Notes

Enhance calculate_overall_health to:
1. Weight by criticality (critical=2, high=1.5, medium=1, low=0.5)
2. If any component is critical, cap at lowest critical score

## Verification

**Commands:**
- Check overall health -- expected: Weighted score

**Manual checks:**
- Critical component caps overall