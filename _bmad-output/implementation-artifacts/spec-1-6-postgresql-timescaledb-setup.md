---
title: 'PostgreSQL + TimescaleDB Setup'
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

**Problem:** The platform needs efficient time-series storage for metrics with fast queries and data compression.

**Approach:** Configure PostgreSQL with TimescaleDB extension, create hypertable for metrics, and set up retention policy.

## Boundaries & Constraints

**Always:**
- Create hypertable with time-based partitioning
- Enable compression for data older than 7 days
- Set retention policy to 90 days

**Ask First:**
- None

**Never:**
- Do not break existing SQLite functionality (for development)

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | TimescaleDB enabled | Hypertable created | N/A |
| HIGH_LOAD | 10k metrics/second | <100ms latency | N/A |
| COMPRESSION | Data >7 days old | 80% storage reduction | N/A |

</frozen-after-approval>

## Code Map

- `backend/app/models/database.py` -- Database connection config
- `docker-compose.yml` -- PostgreSQL + TimescaleDB service

## Tasks & Acceptance

**Execution:**
- [x] `docker-compose.yml` -- Add PostgreSQL + TimescaleDB service -- Time-series database
- [x] `backend/app/models/database.py` -- Support PostgreSQL connection -- Production database
- [x] `init-timescale.sql` -- TimescaleDB initialization script -- Hypertable setup

**Acceptance Criteria:**
- Given PostgreSQL is installed, when TimescaleDB extension is enabled, then the hypertable is created for metrics with time-based partitioning and queries for time-range data use the time index efficiently
- Given TimescaleDB is configured, when 10,000 metrics per second are written, then write latency remains under 100ms and compression reduces storage by at least 80% for data older than 7 days
- Given the database is configured, when retention policy is set to 90 days, then older data is automatically dropped per NFR-RELI-02

## Spec Change Log

<!-- Append-only -->

## Design Notes

For MVP, keep SQLite as default for development. Add PostgreSQL/TimescaleDB config for production.

## Verification

**Commands:**
- Check TimescaleDB extension enabled -- expected: YES

**Manual checks:**
- Verify hypertable exists