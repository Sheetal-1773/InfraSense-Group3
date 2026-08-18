---
status: complete
updated: 2026-08-18
---

# Story 3.2: Alert Generation Service

Status: complete

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Backend Developer,
I want to generate alerts when anomalies are detected,
so that users are notified of issues.

## Acceptance Criteria

1. **Given** an anomaly is detected,
   **When** the alert generation service runs,
   **Then** an alert is created with severity (critical/warning/info)
   **And** the alert includes: component, metric, threshold, current value, timestamp.

2. **Given** an alert is generated,
   **When** the alert is created,
   **Then** the alert status is set to "new".

## Tasks / Subtasks

- [ ] Task 1: Fix anomaly→alert generation in `backend/app/services/alert_service.py` (AC: 1)
  - [ ] `create_alerts_from_anomalies()` — fix recent-anomaly window query (`detected_at >= now` bug)
  - [ ] Remove `Alert.metric` attribute references (attribute does not exist on model — use `metric_id` + embed metric name in title/description)
  - [ ] Map anomaly → alert fields: component_id, severity, threshold, current_value, created_at
  - [ ] Do NOT fabricate time_to_breach / confidence for reactive anomaly alerts (predictive classification is Story 3.8)
- [ ] Task 2: Wire anomaly detection + alert generation into the live background pipeline (AC: 1)
  - [ ] `backend/app/main.py` `background_updater()` — run anomaly detection then `create_alerts_from_anomalies()` each loop
  - [ ] Preserve existing WebSocket `notify_new_alert` broadcast for every newly created alert
  - [ ] Keep `check_and_create_alerts()` (health-based) working — do not remove
- [ ] Task 3: Set new alerts status to "new" and reconcile consumers (AC: 2)
  - [ ] Set `status="new"` on generated alerts (matches Architecture Alerts enum: new/acknowledged/resolved)
  - [ ] Update `backend/app/routers/alerts.py` active-set filters (`in_(["open","acknowledged"])`) to include `"new"` so new alerts surface in list/active/predictive/reactive endpoints
  - [ ] Decide (document in change note) whether Alert.status column default changes from `"open"` or stays for legacy seed rows
- [ ] Task 4: Verify end-to-end (AC: 1, 2)
  - [ ] `python -m py_compile` on edited files
  - [ ] Manual runtime verification (see Testing Standards)

## Dev Notes

### Current State Analysis — files being modified

**`backend/app/services/alert_service.py` (UPDATE — primary file)**
- `AlertService.check_and_create_alerts()` — health-score driven (alerts when `component.health_score < 70`). Called in `main.py:147` each background loop. **KEEP working.**
- `AlertService.create_alerts_from_anomalies(alert_type="reactive")` — the intended anomaly path, but it is **never called** in the live pipeline and contains real bugs:
  - **Bug 1 (line 34):** `Anomaly.detected_at >= datetime.utcnow()` matches only *future* timestamps → returns nothing. Must be a recent window, e.g. `>= datetime.utcnow() - timedelta(minutes=5)`.
  - **Bug 2 (lines 40, 94):** references `Alert.metric` but the `Alert` model (`models.py:133-171`) has **no `metric` attribute** — only `metric_id` FK. Query-build raises `AttributeError` at runtime. Replace with `Alert.metric_id` (nullable) and/or match on component + metric name embedded in title/description.
  - **Bug 3:** fabricates `time_to_breach=random.randint(...)` and `confidence=random.randint(...)` for reactive anomaly alerts. Story 3.2 does not require prediction fields; reactive alerts should leave them `None`. (Predictive classification = Story 3.8.)
  - **Bug 4:** sets `status="active"`; AC requires `"new"`.
- Model `Anomaly` (DB) fields available: `id, component_id, metric_name, value, threshold, threshold_type, severity, detected_at`. Map: `component_id`, `threshold=anomaly.threshold`, `current_value=anomaly.value`, `created_at=now`, `severity=anomaly.severity`, metric via `metric_id` (nullable) or title/description text.

**`backend/app/models/models.py` (UPDATE, optional)**
- `Alert.status` column default = `"open"`; AC requires generated alerts have status `"new"` (matches Architecture enum `new/acknowledged/resolved`). Generate with explicit `status="new"`. Do not silently break legacy rows that use `"open"` (seed data). Document the chosen approach in the change log.

**`backend/app/routers/alerts.py` (UPDATE)**
- `GET /api/alerts` (lines 41-42), `/predictive` (121), `/reactive` (161), `/active` (198) filter `Alert.status.in_(["open","acknowledged"])`. New alerts with `status="new"` would be invisible → add `"new"` to the active set.
- API response shape is `{"data": [...]}` — consumers (check_alerts*.py scripts) expect a bare list and are **stale**; do not rely on them (optional cleanup only).

**`backend/app/main.py` (UPDATE)**
- `background_updater()` currently: metric update → `check_and_create_alerts()` → prediction engine → websocket broadcast. It does **not** run anomaly detection and **not** `create_alerts_from_anomalies()`. Required wiring so AC-1 holds live: call `anomaly_service.run_anomaly_detection(db)` (or per-component `detect_anomalies(..., save=True)`), then `AlertService.create_alerts_from_anomalies()`, then broadcast each new alert via `schedule_websocket(notify_new_alert(alert_to_dict(alert)))` (pattern exists at main.py:148-149).

**`backend/app/routers/anomalies.py` (context — no change required)**
- `POST /api/anomalies/detect/{component_id}` calls `detect_anomalies(..., save=True)` — use it for manual testing of the generation path.

### Architecture Compliance

- **AD-02:** REST stays JSON over HTTP — alert API unchanged.
- **AD-05 Recommendation-Only Remediation:** alert generation must only create alert *records* — the service must never auto-execute remediation or external actions.
- **Architecture Alerts model** (ARCHITECTURE-SPINE.md#Alerts): `id, component_id (FK), severity (critical|warning|info), title, message, time_to_breach, confidence, recommended_action, status (new|acknowledged|resolved), created_at, resolved_at`. AC status `"new"` matches this contract.
- **MVP stack:** FastAPI + SQLAlchemy. **Do not reinvent** — `AlertService` already centralizes create/acknowledge/resolve/deduplicate. Extend it; do not add a parallel alert-creation module.

### Library / Framework Requirements

- Pin changes: **none**. `backend/requirements.txt` has `fastapi==0.109.0`, `sqlalchemy==2.0.25`, `pydantic==2.5.3`. Use existing versions.
- No new package needed for this story.
- Python 3.12 note: `datetime.datetime.utcnow()` is deprecated → prefer `datetime.now(timezone.utc)` in new code where trivially possible (existing codebase uses naive `utcnow` consistently — at minimum do not expand deprecation surface).

### File Structure Requirements

- Add/edit only under `health-analytics-platform/backend/app/`:
  - `services/alert_service.py` (primary)
  - `services/anomaly_service.py` (reuse existing entrypoints — no new module)
  - `main.py` (background wiring)
  - `routers/alerts.py` (status filter reconciliation)
  - `models/models.py` (status default decision, if made)
- Follow existing conventions: snake_case modules, classes injected with `Session`, router prefix `/api/alerts`, module-level singletons via `_service = None; get_service()` (see `alert_generator.py`, `notification_service.py`) when shared.
- Story/artifact output lives in `_bmad-output/implementation-artifacts/`.

### Testing Standards

- **No pytest/automated test harness exists in this repo.** Verification is manual (see prior spec stories):
  - `python -m py_compile` on all edited `.py` files.
  - Start backend (`python run.py` from `health-analytics-platform/backend`; seed data via `ENABLE_SEED_DATA=true` or mock mode).
  - Trigger anomaly: `POST /api/anomalies/detect/{component_id}` with a seeded component id, then `GET /api/alerts` → confirm a new alert row includes `component_name`, metric/threshold/current_value (title/description), `severity`, `created_at`, `status`.
  - AC 2: confirm generated alert `status` field == `"new"` and that it appears in `GET /api/alerts` / `/active`.
  - Do NOT use `check_alerts.py` / `check_alerts2.py` / `check_severity.py` as tests — they assume a bare-list response that the API does not return (`{"data": [...]}`).

### Project Structure Notes

- Backend layout: `health-analytics-platform/backend/app/{models,services,routers,schemas}`. Source-tree align: put generation logic under `services/`, queries under the same service.
- Story files for prior backend work are tracked in `_bmad-output/implementation-artifacts/` (e.g. `spec-3-1-static-threshold-detection.md`, `spec-2-1-*.md`). This story follows that location.
- No naming conflicts: existing `3-2-predictive-alert-card.md` is a separate frontend artifact; do not modify frontend code for this story.

### References

- [Source: `_bmad-output/planning-artifacts/epics.md#Story 3.2` — story statement + acceptance criteria]
- [Source: `_bmad-output/planning-artifacts/architecture/.../ARCHITECTURE-SPINE.md#Alerts` — data model & status enum; `#AD-02`; `#AD-05`]
- [Source: `_bmad-output/planning-artifacts/prds/.../prd.md#6.9 Alerting (FR-ALERT)` — FR-ALERT-01..05]
- [Source: `_bmad-output/implementation-artifacts/spec-3-1-static-threshold-detection.md` — prior story, created `anomaly_service.py`]

## Dev Agent Record

### Agent Model Used

deepseek-v4-flash-free (BMad create-story workflow)

### Debug Log References

- Sprint status: `_bmad-output/implementation-artifacts/sprint-status.yaml` (target `3-2-alert-generation-service: backlog`)

### Completion Notes List

- Ultimate context engine analysis completed — comprehensive developer guide created

### File List

- `_bmad-output/implementation-artifacts/3-2-alert-generation-service.md` (this file)