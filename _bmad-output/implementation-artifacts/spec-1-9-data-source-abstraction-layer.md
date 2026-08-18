---
title: 'Data Source Abstraction Layer'
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

**Problem:** The platform needs a data-source abstraction layer so different monitoring sources can be integrated without changing core logic.

**Approach:** Update core services to use the DataSourceAdapter interface instead of direct database queries.

## Boundaries & Constraints

**Always:**
- Core services use DataSourceAdapter interface
- Normalized response format regardless of data source
- Easy to add new data sources

**Ask First:**
- None

**Never:**
- Do not break existing functionality

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | Query through abstraction | Normalized response | N/A |
| SOURCE_SWAP | Swap mock to real | No downstream changes | N/A |

</frozen-after-approval>

## Code Map

- `backend/app/services/data_sources/__init__.py` -- Already created in 1-8
- `backend/app/services/health_service.py` -- Update to use abstraction

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/services/health_service.py` -- Use DataSourceAdapter -- Abstraction integration

**Acceptance Criteria:**
- Given the abstraction layer is implemented, when a new data source is added, then it implements the standard interface (fetch_components, fetch_metrics, fetch_health) and the core services consume data through the abstraction without knowing the source
- Given the abstraction layer exists, when I query for components, then I get a normalized response regardless of the underlying data source

## Spec Change Log

<!-- Append-only -->

## Design Notes

The base interface was created in story 1-8. This story ensures health_service uses it.

## Verification

**Commands:**
- Check health service uses adapter -- expected: Yes

**Manual checks:**
- Verify normalized response format