---
title: 'Configurable Health Thresholds'
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

**Problem:** The platform needs configurable health thresholds per component type.

**Approach:** Create thresholds API endpoint to manage threshold configuration.

## Boundaries & Constraints

**Always:**
- Update thresholds per component type
- Validate warning < critical
- New scores use updated thresholds

**Ask First:**
- None

**Never:**
- Do not recalculate existing scores

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | Valid threshold update | 200 OK, thresholds updated | N/A |
| ERROR_INVALID | warning > critical | 400 Bad Request | N/A |

</frozen-after-approval>

## Code Map

- `backend/app/models/models.py` -- Threshold model (exists)
- `backend/app/routers/thresholds.py` -- Create new router

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/routers/thresholds.py` -- Create thresholds API -- CRUD operations

**Acceptance Criteria:**
- Given the threshold configuration API exists, when a user updates thresholds for "server" components, then new health scores use the updated thresholds and existing scores are not recalculated
- Given threshold configuration, when invalid values are provided (e.g., warning > critical), then a 400 error is returned with validation message

## Spec Change Log

<!-- Append-only -->

## Design Notes

Threshold model exists in models.py. Need to create router for CRUD operations.

## Verification

**Commands:**
- Update threshold -- expected: 200 OK

**Manual checks:**
- Invalid values return 400