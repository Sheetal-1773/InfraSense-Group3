# Rubric Review — Architecture Spine (InfraSense) v2.0, re-derived 2026-08-17

**Reviewer:** Rubric walker (Reviewer Gate)
**Scope:** ARCHITECTURE-SPINE.md vs. implemented `health-analytics-platform` codebase and driving PRD
**Method:** Read the spine, then reality-checked every AD, the consistency conventions, the stack table, the source tree, and the deferred/open lists against the code (`main.py`, `routers/*`, `services/*`, `models/models.py`, `docker-compose.yml`, `package.json`, `requirements.txt`, `Dockerfiles`), plus the PRD.

---

## Verdict

**CONDITIONAL — the paradigm flip (monolith ratification) is correct and the stack table is verified current, but the spine is not a clean ratification of implemented reality.** Several Rules contradict live code — including three that are the exact divergences those ADs claim to prevent (alert status vocabulary, prediction hierarchy binding a non-conforming generator, and a WebSocket contract whose `/ws/predictions` route does not exist) — and the operational/security envelope from the PRD (NFR-SEC, NFR-COMP, retention, environments) is left entirely silent. Fix the 2 Critical + 2 High findings below and re-ratify; the rest are low-cost accuracy corrections.

---

## Checklist scores

1. **Fixes real divergence points, misses none** — ❌ Misses at least four live divergences: dual runtime writers, `/ws/predictions` contract gap, `active`/`open` status drift, and a bound `PredictionGenerator` that violates AD-01.
2. **Every AD Rule enforceable and prevents its stated divergence** — ❌ AD-07, AD-08, AD-01 fail; AD-05 is vacuous.
3. **Nothing under Deferred could let two units diverge** — ⚠️ Largely sound; one gap: the anomaly "detect endpoint exists (manual)" claim is true, but the deferred items omit the unactive TimescaleDB hypertable/retention (two units could diverge on what "90-day retention" means).
4. **Named tech verified current (code + web)** — ✅ Verified against `package.json`/`requirements.txt`/`Dockerfiles`: Python 3.11-slim, FastAPI 0.109.0, Uvicorn 0.27.0, SQLAlchemy 2.0.25, Pydantic 2.5.3, NumPy 1.26.3, React 18.3.1, Vite 8.2.0, TS 5.9.3, React Router 7.18.2, Recharts 3.10.1, TanStack Query 5.101.4, Tailwind 4.3.3, Node 20-alpine, timescaledb:latest-pg16. One error in Deferred reasoning (Prophet never in requirements).
5. **Ratifies rather than contradicts** — ⚠️ Ratifies the paradigm correctly but contradicts code in the four places below.
6. **Covers driving PRD capabilities** — ⚠️ FR coverage is complete and well-mapped; NFR coverage (SEC/COMP/RELI/DATA) is largely absent.
7. **Every dimension the altitude owns decided/deferred/open** — ❌ Security, compliance, environments, and operations are silent; correlation/blast-radius behavior has no governing AD.

---

## Critical

### C1 — AD-08 ratifies the wrong alert vocabulary; the exact drift it claims to prevent is live in the code
**Spine:** ARCHITECTURE-SPINE.md:107 ("`open` is the single new-alert status") and :130 (consistency convention `open/acknowledged/resolved`).
**Code reality:** new alerts are created with status **`active`**, not `open`:
- `services/alert_service.py:63` and `:151` (`status='active'`)
- `services/alert_generator.py:196` (`status: "active"`)
- `routers/alerts.py:39` (`_persist_dynamic_alert` writes `status="active"`)
- `services/seed_service.py:231,438` (`active`) **and** `:339,379` (`open`) — both vocabularies are seeded
- Consumers query **`open`**: `routers/alerts.py:155,195,232` filter `status.in_(["open","acknowledged"])`.

Consequence: an alert written `active` by `AlertService` will not appear in `GET /api/alerts/active` (which queries `open`/`acknowledged`). The two-vocabulary drift AD-08 states it "prevents" exists and is demonstrable. The spine has ratified the vocabulary the producers do **not** use.
**Rationale:** Rule is not enforceable and does not prevent its stated divergence — it encodes a target the code contradicts. Also note the rule's dedup clause ("one open alert per component+metric") is not implemented: `_create_alert_for_component` dedupes on `component_id` only (`alert_service.py:129-135`), and `deduplicate_alerts` is never invoked in the background loop.

### C2 — AD-07 ratifies a WebSocket contract whose `/ws/predictions` channel does not exist, breaking real-time prediction delivery to the UI
**Spine:** ARCHITECTURE-SPINE.md:97 ("pushes changes over WebSocket channels `/ws/health`, `/ws/alerts`, `/ws/predictions`").
**Code reality:** `routers/websocket.py` defines only `/ws`, `/ws/alerts`, `/ws/health` (lines 8, 24, 34). There is **no** `/ws/predictions` route. The `predictions` channel exists only as a broadcast bucket in `ConnectionManager` (`services/websocket_manager.py:16`) reachable via the generic `/ws?channel=predictions`, which the frontend does not use.
The frontend connects to `/ws/predictions`: `src/hooks/useWebSocket.ts:43` builds `${wsUrl}/ws/${channel}` and `:240-244` calls `useWebSocket({ channel: 'predictions' })`. `useLivePredictions` will fail to connect, so predictions never stream to the dashboard — exactly the "UI and DB state disagreeing" outcome AD-07 says it prevents.
**Rationale:** The spine's own stated contract is not implemented; a divergence the AD is supposed to fix is missed. (Also note `metrics_update` is emitted by the collector, not the background thread — see H1.)

---

## High

### H1 — AD-07's "single runtime mutation driver" is false: the async `MetricCollector` is a second writer
**Spine:** ARCHITECTURE-SPINE.md:27 ("One background thread is the single mutation driver") and :97 ("The background updater thread ... is the single runtime mutation driver").
**Code reality:** there are **two** runtime writers:
- `main.py:122-159` `background_updater` thread (registers components, health, alerts, predictions, broadcasts health/alert/prediction).
- `services/collectors/metric_collector.py:49-78` — an **asyncio task** running in the event loop that writes `ComponentMetric` rows (`_store_metrics_sync`, :83-116), **creates components** (`_create_component_from_discovered`, :118-151), and broadcasts `metrics_update` on the health channel (:158-170).

Both are started in the lifespan when `ENABLE_REAL_COLLECTION=true` (the default; the compose backend runs with the collector active since `DATA_MODE=mock` does not disable it — `main.py:211-218`, `main.py:26`). Two independent write paths to `components`/`component_metrics` can diverge (e.g., `source` hardcoded to `"simulated"` in `metric_collector.py:103` vs. manager-tagged sources).
**Rationale:** The spine missed a real divergence point (dual writers) and instead ratified a single-writer claim the code contradicts. The rule as written cannot be enforced because it omits the collector entirely.

### H2 — AD-01 binds `PredictionGenerator`, which violates the very hierarchy and floors the rule mandates
**Spine:** ARCHITECTURE-SPINE.md:33 (binds both `PredictionEngine` and `PredictionGenerator`) and :37 (static ≥70 / dynamic ≥60 / trend ≥50, "never a low-confidence estimate").
**Code reality:** `PredictionGenerator` (`services/prediction_generator.py`) does **not** implement the static→dynamic→trend hierarchy at all. It uses fixed usage gates (`cpu > 60`, `memory > 60`, `disk > 70`, `latency > 300`, `error_rate > 2`) with confidence as low as **50-60** (`:35,57,79,101,123,144`), and prediction types like `cpu_failure`/`health_degradation` — no floors, no hierarchy, no "insufficient history" path. It is **live**, not dead code: `routers/predictions.py:25-26` and `:152-153` call `get_prediction_generator()` on `GET /api/predictions` and `/generate`, and those dynamic predictions are served to the UI merged with DB predictions (`:51-72`).
**Rationale:** A component the AD explicitly binds produces predictions below the mandated confidence floors and outside the mandated evaluation order. The Rule is not enforceable on the bound set; the spine either mis-binds `PredictionGenerator` or must extend the rule to cover (or explicitly exempt/defer) it.

### H3 — PRD NFR-SEC and NFR-COMP are entirely silent — no decision, defer, or open question
**Spine:** no mention of security or compliance anywhere (checked all ADs, Deferred, Open Questions, Consistency Conventions).
**PRD:** NFR-SEC-01 TLS encryption in transit (Must), NFR-SEC-02 RBAC (Must, V3), NFR-SEC-03 audit logging for admin actions (Must), NFR-SEC-04 encryption at rest (Should), NFR-SEC-05 on-premises deployment (Should); NFR-COMP-01 DORA (Should), NFR-COMP-02 NIS2 (Should), NFR-COMP-03 GDPR handling (Must), NFR-COMP-04 audit trail for predictions (Must). `rbac/multi-tenancy` is deferred, but TLS/audit/encryption/compliance are not decided, deferred, or opened anywhere.
**Code note:** the API runs plain HTTP with `CORSMiddleware(allow_origins=["*"], allow_credentials=True)` (`main.py:228-234`) and no auth; this is fine to defer for MVP, but the spine must say so. A whole security/compliance dimension left silent is a checklist-item-7 finding.
**Rationale:** The initiative altitude owns the operational/environmental envelope; silence here means two future units (e.g., a frontend proxy and the API) have no binding constraint on transport security.

### H4 — No decision on environments and operations (retention, backups); TimescaleDB hypertable/retention is aspirational, not active
**Spine:** AD-09 covers topology; nothing covers environments (dev/staging/prod), operations, or data retention.
**Code reality:** `database.py:84-95` defines `init_timescaledb()` (hypertable conversion + compression + retention) but it is **never called**; `main.py` imports only `engine, Base, SessionLocal` from it. `init-timescale.sql` has hypertable/compression/retention statements **commented out** ("run these commands to convert"). So on the shipped compose stack, `component_metrics` is a plain table, not a hypertable, and the PRD's NFR-RELI-02 (90-day retention) and NFR-DATA (data residency) are unenforced. The Deferred table does not flag this.
**Rationale:** Two units could diverge on what "90-day retention" means (no policy exists), and the ops envelope is silent. This should be a Deferred row or Open Question at minimum.

---

## Medium

### M1 — AD-01's fallback surface string "Prediction unavailable — insufficient history" exists nowhere
The string appears in neither backend nor frontend (searched `*.py` and `src/`). `PredictionEngine` simply returns `None` from `_predict_for_component` (`prediction_service.py:40-41`) and the UI renders nothing. The rule mandates a user-facing behavior that is not implemented; as a ratification of reality the phrase is aspirational. Either implement it or soften the rule to "no prediction is produced below floor."

### M2 — Correlation and blast radius (FR-CORR, FR-BLAST) have no governing AD; the capability map misattributes them to AD-06
ARCHITECTURE-SPINE.md:261 maps correlation/blast-radius to AD-06, whose rule (don't branch on source identity) regulates nothing about correlation semantics (dedup, ranking, root-cause probability, blast radius, persistence). There is no decision, deferral, or open question covering how correlations behave. `correlation_engine.py`/`correlations.py` compute on-demand in the request path (never in the background loop), and `correlation_service.py` (DB persistence) is not wired anywhere. The altitude owns this behavior; it is currently decided-by-absence.

### M3 — AD-09 overstates the compose topology: demo apps are a separate stack
ARCHITECTURE-SPINE.md:117 and the Deployment mermaid (:190-202) present customer/payment/auth APIs as part of "the" docker-compose deployment. Reality: `docker-compose.yml` has only `postgres`/`backend`/`frontend`; the demo apps live in a separate `applications/docker-compose.yml` (ports 4000/4001/4002) on their own network. Also the frontend service runs `npm run dev` (Vite dev server) rather than a built SPA. The AD's rule ("ships as a modular monolith under docker-compose" including demo targets) is a mild overstatement of the actual shipped topology.

### M4 — Source Tree omits files bound by ADs
The tree (ARCHITECTURE-SPINE.md:238-250) omits `data_source_manager.py`, `websocket_manager.py`, `metric_normalizer.py`, `metric_catalogue.py`, `correlation_service.py`. `data_source_manager` and `websocket_manager` are explicitly named in AD-06/AD-07 binds; an implementing team reading the tree would not find them. Minor but cheap to fix.

### M5 — Envelope/pagination convention partially contradicted
ARCHITECTURE-SPINE.md:128 states list endpoints return `{"data": [...]}`. `GET /api/alerts` and `GET /api/predictions` comply, but `GET /api/anomalies` (`routers/anomalies.py:42`) and `GET /api/correlations` return bare arrays, and several `GET /{id}` handlers in `routers/alerts.py` return non-enveloped objects (fine) — the convention should either list the exceptions or be scoped to "list endpoints" that comply.

---

## Low

### L1 — AD-05's guard is never invoked; the Rule is vacuous
`remediation_guard.py` is not imported or called anywhere (searched all `*.py`). The invariant "no auto-remediation" holds today only by absence of remediation code, not by the guard "blocking on every path." The Rule overstates an enforcement mechanism that does not exist; reframe as "no auto-remediation exists; any future remediation path must pass through `remediation_guard`."

### L2 — Deferred reason for ML is inaccurate on Prophet
ARCHITECTURE-SPINE.md:270 says scikit-learn/Prophet are "declared in requirements, unused." `requirements.txt` pins `scikit-learn==1.4.0` and `pandas==2.1.4` (both unused), but **Prophet is not in requirements** (and nothing imports it). Correct the row to name scikit-learn/pandas.

### L3 — AD-03's <2% CPU / <100MB bound has no measurement
The constraint is a stated aspiration; no code measures collection overhead, so the Rule is not enforceable/testable. Acceptable as a ratified intent, but note it is currently unverifiable and there is no load/monitoring hook to ever verify it.

### L4 — AD-06 source tagging leaks on stored metrics
Components are tagged with `source`/`provider` by the manager, but every `ComponentMetric` written by the collector hardcodes `source="simulated"` (`metric_collector.py:103`). AD-06's normalized-data tagging is only partially true at the metric layer.

---

## Notes on what is done well (verified clean)

- **Paradigm flip is correct:** single FastAPI process, routers thin, services carry logic, shared SQLAlchemy schema, WebSocket push, docker-compose monolith. All verified against `main.py`, `routers/*`, `services/*`.
- **AD-02 (JSON/HTTP only):** no gRPC/proto files exist; per-channel WebSockets are the only non-REST protocol. Accurate.
- **AD-03/AD-04/AD-06 seams:** adapter interface (`data_sources/base.py`) and manager dedupe-by-id + source/provider tagging exist as described; downstream services do consume adapter data. Accurate modulo L3/L4.
- **AD-09 core claim (no K8s/Kafka/cloud today):** accurate; all three correctly deferred.
- **Stack table:** every pinned version matches `requirements.txt`/`package.json`/Dockerfiles, including Vite 8.2 and Tailwind 4.3.
- **10-table schema and ER diagram:** match `models/models.py` exactly (including `PREDICTION ||--o{ ALERT` via `prediction_id`, `ALERT ||--o{ ALERT` via `parent_alert_id`).
- **Deferred list is largely honest and code-accurate** (OTel draft, Prom remote-write endpoint present but unrouted, escalation/webhook/email modules implemented-but-not-invoked, anomaly detection manual-only, RBAC/multi-tenancy deferred).

---

## Recommended disposition

1. C1: rewrite AD-08 to either (a) ratify `active` as the new-alert status and align the routers, or (b) declare the vocabulary a deliberate divergence target with a concrete migration row in Deferred. Also fix the `_create_alert_for_component` dedup to component+metric.
2. C2: add `/ws/predictions` to `routers/websocket.py` (or route the frontend through `/ws?channel=`), then re-state AD-07's channel list to match what actually ships.
3. H1: extend AD-07's binds/rule to include `metric_collector` and define the ownership boundary between collector writes and updater writes (or collapse to one writer).
4. H2: unbind `PredictionGenerator` from AD-01 or govern it explicitly (defer its outputs, or extend the hierarchy rule to cover it).
5. H3/H4: add an AD or a Deferred/Open-Question row set covering transport security, RBAC, audit, retention/hypertable activation, and environment strategy — closing the silent dimensions.
6. Apply M1-M5/L1-L4 accuracy fixes and re-ratify.
