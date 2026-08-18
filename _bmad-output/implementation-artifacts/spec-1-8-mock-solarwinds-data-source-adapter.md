---
title: 'Mock SolarWinds Data Source Adapter'
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

**Problem:** Development and testing need a mock SolarWinds API adapter since real SolarWinds is not available.

**Approach:** Create a mock adapter that returns realistic mock data for servers, databases, networks, and applications with time-series patterns.

## Boundaries & Constraints

**Always:**
- Return realistic mock data for all component types
- Include time-series data with trends, spikes, and normal variation
- Follow data-source abstraction interface

**Ask First:**
- None

**Never:**
- Do not make actual SolarWinds API calls

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | Query components | List of mock components | N/A |
| HAPPY_PATH | Query metrics | Time-series data with patterns | N/A |

</frozen-after-approval>

## Code Map

- `backend/app/services/data_sources/base.py` -- Base adapter interface
- `backend/app/services/data_sources/solarwinds_mock.py` -- Mock implementation

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/services/data_sources/base.py` -- Base adapter interface -- Data source abstraction
- [x] `backend/app/services/data_sources/solarwinds_mock.py` -- Create mock adapter -- Realistic mock data

**Acceptance Criteria:**
- Given the mock SolarWinds adapter is implemented, when the adapter is queried for component data, then it returns realistic mock data for servers, databases, networks, and applications
- Given the mock adapter is running, when metrics are requested for a component, then the adapter returns time-series data with realistic patterns (trends, spikes, normal variation)
- Given the data-source abstraction layer exists, when the mock adapter is swapped for a real SolarWinds adapter, then no changes are required to the downstream health scoring or prediction engines

## Spec Change Log

<!-- Append-only -->

## Design Notes

Mock data should include realistic patterns: baseline, gradual increase, occasional spikes.

## Verification

**Commands:**
- Query mock adapter -- expected: Realistic data returned

**Manual checks:**
- Verify data patterns look realistic