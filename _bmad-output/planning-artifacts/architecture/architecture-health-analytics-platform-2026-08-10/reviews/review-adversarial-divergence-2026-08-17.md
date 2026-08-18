---
title: "Adversarial Divergence Review — ARCHITECTURE-SPINE.md v2.0 (InfraSense Health Analytics Platform)"
reviewer: "Adversarial Divergence Reviewer (Reviewer Gate)"
date: "2026-08-17"
spine: "ARCHITECTURE-SPINE.md (updated 2026-08-17, re-derived from health-analytics-platform)"
method: "Construct two one-level-down units that each obey every AD-01..AD-09 and every Consistency Convention to the letter, yet build incompatibly. Every pair found = a hole."
verdict: "REJECT (re-open for amendments)"
---

# Verdict

**The spine as written does not prevent divergence; it certifies three existing divergences already present in the codebase it was re-derived from.** The strongest evidence is that the *current* implementation — the very source the spine claims to ratify — contains at least two alert status vocabularies (`active` vs `open` vs `escalated`), two prediction engines with incompatible confidence semantics and prediction-type vocabularies, and two web-socket mutation drivers, all simultaneously "AD-compliant." A future builder one level down reading only this spine would reproduce these splits (or pick sides), producing an incompatible build. The spine needs 2 new ADs (component identity/source vocabulary; entity write-ownership) and amendments to AD-01, AD-07, AD-08, AD-09, plus tightened Consistency Convention rows before it can gate downstream work.

Findings below are tiered Critical / High / Medium / Low. Each names the concrete diverging pair, the hole it exposes, and the suggested fix.

---

# CRITICAL

## C-1 — AD-01 defines the ladder and the floors but not "confidence" — two prediction engines both comply and disagree on everything downstream

**Diverging pair:**

- **Unit A — `PredictionEngine`** (`services/prediction_service.py`): interprets *confidence as fit quality* — static level derives it from R² (`prediction_service.py:110`), dynamic level from history length (`prediction_service.py:159`), trend level from R² (`prediction_service.py:197`). Emits `prediction_type ∈ {static, dynamic, trend}`. On failure of all levels it returns nothing and the "Prediction unavailable" message is invisible to the API (the list endpoint simply shows fewer rows).
- **Unit B — `PredictionGenerator`** (`services/prediction_generator.py`): interprets *confidence as a severity-scaled heuristic* that is monotone in current utilization (`confidence = 60 + (cpu-60)*0.8`, etc.). Emits `prediction_type ∈ {cpu_failure, memory_failure, disk_failure, latency_failure, error_failure, health_degradation}`. It always emits when any hard-coded branch fires (cpu>60, mem>60, disk>70, latency>300, error_rate>2, health<70) and has no "unavailable" path.
- A third writer, `seed_service.seed_predictions`, uses yet another vocabulary (`'Disk Usage'`, `'Memory Usage'`, `'CPU Usage'`).

Both units obey AD-01's literal text: simple-first evaluation order, floors ≥70/60/50, ML deferred. Yet for the same component+metric they produce different predictions, different `prediction_type` values, and different availability behavior.

**The hole:** AD-01 fixes the *ordering* and *floors* but leaves (a) the *meaning of confidence* (fit quality vs severity), (b) the `prediction_type` vocabulary, (c) the *single producer* of persisted `Prediction` rows, and (d) the "insufficient history" representation at the API, all unconstrained. A builder of a downstream consumer (e.g., the AD-08 predictive-alert→prediction linker, which matches on `prediction_id`) cannot rely on `prediction_type` or `confidence` meaning the same thing across producers. Additionally `PredictionEngine` contains a *hidden floor rewrite* — `if confidence < 70 and time_to_breach > 5: confidence = 70` (`prediction_service.py:112`) — which a second implementer of the same engine would not reproduce, so even two copies of "the compliant engine" diverge on identical data.

**Fix (amend AD-01, or new AD "Prediction Contract"):**
1. Define confidence semantically: "probability in [0,100] that the component crosses the threshold within `time_to_breach_minutes`," and explicitly forbid severity-scaled confidence.
2. Canonicalize the `prediction_type` vocabulary and ban ad-hoc values.
3. Declare a single writer: only the background-updater step may create/refresh `Prediction` rows; `POST /api/predictions/run`, `POST /api/predictions/generate`, and `seed_predictions` in steady state are violations.
4. Specify the API-level "Prediction unavailable" representation (omission vs explicit marker) so two consumer builders can't diverge.

---

## C-2 — AD-08 is self-contradictory: the single-status vocabulary it mandates is not the vocabulary the code it binds writes — two alert producers write different statuses and break the one-open-alert invariant

**Diverging pair:**

- **Unit A — `AlertService.check_and_create_alerts`** (`services/alert_service.py:128-158`) and the **dynamic-alert persistence path** in `routers/alerts.py:25-45` write `status='active'`, and dedup on `(component_id, status=='active')` — *ignoring metric entirely*.
- **Unit B — `seed_service.seed_alerts`** (`services/seed_service.py:313-382`) writes `status='open'` and dedups on `(component_id, status in ['open','acknowledged'])`.
- **Unit C — `EscalationService`** (`services/escalation_service.py:73`) writes `status='escalated'` and queries `['active','acknowledged']` (`escalation_service.py:37`).
- **Unit D — the alert read paths** disagree too: `get_active_alerts`/`/api/alerts/active` filter `['open','acknowledged']` (`alerts.py:232`, `alert_service.py:211`), while escalation and the alert list filter `['active','acknowledged']`.

All four units read AD-08's text — "Lifecycle is `open → acknowledged → resolved`", "`open` is the single new-alert status", Consistency row "Single vocabulary: open/acknowledged/resolved" — and all four are in the current codebase. `active` (written by the runtime path the spine binds: `alert_service`, `alert_generator`, alert routers) appears nowhere in the spine's vocabulary; `escalated` likewise.

**The hole:** AD-08 prevents "status-vocabulary drift" and "duplicate alerts for one condition" and yet (1) sanctions two coexisting vocabularies by binding code that writes `active` while declaring `open` the only new-alert status; (2) the dedup key is underspecified — AD-08 says "one open alert per component+metric" but `AlertService` dedups on `(component, active)` and seed on `(component, open/acknowledged)`, neither keyed on `metric`, so a health alert and a metric alert coexist, or one stale `active` row silently blocks future alerts; (3) `Alert.metric` (used by dedup and referenced in `alert_service.py:38,65,95`) is absent from the spine's ER diagram, so a builder implementing the ER model cannot even do the mandated dedup; (4) reactive alerts are created with `confidence=random(60,90)` and `time_to_breach=random(15,120)` (`alert_service.py:66-67,155-156`) — predictive fields on reactive alerts, precisely the mis-prioritization AD-08 claims to prevent, because AD-08 never forbids it.

**Fix (amend AD-08):**
1. Declare the canonical set `{open, acknowledged, resolved}` only; forbid `active` and `escalated` as statuses (escalation becomes timestamp/count fields, not a status — the columns already exist).
2. Define the dedup key precisely: `(component_id, metric)` for one open/acknowledged alert, and make `Alert.metric` a mandatory column (add it to the ER diagram).
3. State that reactive alerts carry no `confidence` and no `time_to_breach`.

---

# HIGH

## H-1 — AD-07's "single mutation driver" is bypassed by every component that already exists — and by any new service the Deferred table invites

**Diverging pair:**

- **Unit A — `background_updater` thread** (`main.py:122-159`), AD-07's named single driver.
- **Unit B — `MetricCollector`** (`services/collectors/metric_collector.py:83-171`): a *second* runtime driver on the asyncio loop that writes `ComponentMetric` rows, creates `Component` rows (`_create_component_from_discovered`, `:118-151`), and broadcasts `metrics_update`.
- **Unit C — HTTP endpoints that mutate state**, directly contradicting AD-07's own sentence "HTTP endpoints only read or act on user intent (acknowledge/resolve); they never mutate metric state": `POST /api/v1/metrics` and `POST /api/v1/write` write metric rows (`routers/metrics.py:62-150`); `POST /api/components` (`routers/components.py:15`), `POST /api/components/refresh-all` (`:285-290`), `POST /api/predictions/run` (`routers/predictions.py:217-221`), `POST /api/predictions/cleanup` (`:207-214`), and `POST /api/data-mode` (`main.py:296-304`) all mutate state outside the driver.
- **Unit D — a future service.** The Deferred table says anomaly detection should "run continuously per FR-AND" and notification should be "wire[d] behind ... the background loop" — two legal homes. Builder D1 inserts a continuous anomaly loop into `background_updater`; builder D2 adds it as its own collector-style task (as `MetricCollector` already does). Both comply with AD-07 as written; two loops then write anomalies + alerts concurrently.

**WS divergence under the same AD:** AD-07 lists channels `/ws/health`, `/ws/alerts`, `/ws/predictions` and message types including `metrics_update`, but there is no `/ws/metrics` channel; the collector broadcasts `metrics_update` onto the `health` channel with its *own* envelope (`metric_collector.py:158-171`) while the manager wraps `{type, data, timestamp}` (`websocket_manager.py:51-80`). A WS-consumer builder cannot know which channel carries `metrics_update` or what envelope to expect.

**The hole:** AD-07 binds two specific objects and names a pipeline order, but gives no mutation taxonomy (which state classes only the driver may write), no registration mechanism for new continuous services, and no channel/message matrix.

**Fix (amend AD-07):**
1. Add a mutation taxonomy: metric rows, component registration, component status/health, alert creation, and prediction creation are driver-owned; HTTP may only acknowledge/resolve/escalate and change settings.
2. Either fold continuous services (anomaly) into the updater step list or grant an explicit second-driver carve-out with its own ownership; "somewhere in the background" is not a rule.
3. Add a WS channel × message-type matrix (who may broadcast, exact envelope) and either add `/ws/metrics` or re-state that `metrics_update` rides the health channel.

---

## H-2 — AD-06 leaves component identity and the source vocabulary undefined — two adapters collide, and two consumers of "the abstraction" read different sources

**Diverging pair:**

- **Unit A — an adapter author** following the AD-06 interface (`data_sources/base.py`): each adapter in the codebase stamps its *own* `source`: local → `"psutil"` (`local_adapter.py:46,59`), simulator → `"simulator"` (`simulator_adapter.py:60`), mock → `"mock"` (`solarwinds_mock.py:46`).
- **Unit B — `DataSourceManager.discover_components`** (`data_source_manager.py:71-112`): overwrites every component's `provider`/`source` with manager-owned values (`local`/`local`, `simulated`/`simulated` — the simulator *and* the mock both become `simulated`).
- **Unit C — the consumers that AD-06 says "must not branch on source identity"** demonstrably do: `/api/components/by-source` (`routers/components.py:190-229`), `/api/components/infrastructure/summary` (`:412-473`, mapping `mock|simulator → simulated`).

So the same component surfaces with two different `source` values depending on which boundary is read, the `source` vocabulary is undefined (`psutil`/`system`/`local`/`simulator`/`simulated`/`mock` all appear), and no builder can enumerate it.

**ID collision:** AD-06 dedups by component id but imposes no id namespacing. A real SolarWinds adapter and the mock both emit `prod-web-01` (`solarwinds_mock.py:27`); the manager's first-wins dedup (`data_source_manager.py:82-83,95-96,106-107`) silently drops one or attributes data to the wrong source. Separately, four writers create `Component` rows under four id vocabularies: `local-<host>-*`, `sim-*`, `prod-*`/`customer-api-prod`, `comp-*` (`seed_service.py:51`), and raw `uuid4` (`components.py:36`). The Consistency ID row prefixes alert/prediction/anomaly/correlation ids but is silent on the component id — which is the join key for every other entity.

**Fix (new AD-10 "Component Identity & Source Vocabulary", or amend AD-06):**
1. Adapters must emit namespaced component ids (`<source-ns>/<type>/<name>`) or be rejected by the manager; add a test asserting no cross-adapter id collisions.
2. Canonicalize the `source`/`provider` vocabulary and declare a single tagging owner (the manager); adapters must not stamp `source`.
3. Declare the single registration/write owner of the `Component` entity (see H-3), closing the four-writer hole.

---

## H-3 — AD-09's "extraction without rework" promise is unenforceable: no entity has a single owner, and the "abstraction" is two separate singletons

**Diverging pair:**

- **Unit A — a builder who extracts the alert service** on the strength of AD-09 ("service boundaries are the routers+services seams, preserved so any service can be extracted without rework") and of the "two owners of one entity" principle the spine does not cover.
- **Unit B — the shared-schema reality**: `Alert` rows are written by `alert_service.py`, `seed_service.py`, and directly by `routers/alerts.py` (`_persist_dynamic_alert`, `:25-45`); `Prediction` by `prediction_service.py`, `seed_service.py`, and `POST /api/predictions/run`; `Component` by four writers (H-2). Extracting any service forces ownership carving and dedup/lifecycle rework that AD-09 says will not be needed.
- **Unit C vs Unit D — split singletons**: `health_service.get_data_adapter()` (`health_service.py:13-18`) imports `get_data_source()` from the `data_sources` package → a module-level `MockSolarWindsAdapter`; `DataSourceManager.get_primary_adapter()` (`data_source_manager.py:61-69`) → its *own* singleton mock. Two "consumers of the adapter abstraction" (AD-06) hold separate adapter instances with separate in-memory metric histories → the same component id yields two divergent metric streams and two health scores.

**The hole:** AD-09 asserts a property (extraction without rework) without the precondition that makes it true (single write-owner per entity) and AD-06 asserts "one normalized view" while two singletons each own a view. Both are unverifiable as written — a reviewer cannot falsify them from the spine, and two builders comply while building incompatible splits.

**Fix (amend AD-09, or new AD "Entity Ownership Matrix"):**
1. Add a per-entity write-ownership table (Component / ComponentMetric / Prediction / Alert / Anomaly / Correlation / Threshold / Settings) with exactly one writer per entity.
2. Mandate a single process-wide adapter registry (one `DataSourceAdapter` instance per source), killing the split-singleton divergence.
3. Make extraction conditional: a service is extractable only once its entity ownership is exclusive; until then "extraction without rework" is marked deferred.

---

# MEDIUM

## M-1 — Consistency Conventions "Envelopes" row is false for half the list endpoints

**Diverging pair:** endpoints returning `{"data": [...]}` (`/api/components`, `/api/alerts`, `/api/predictions`, `routers/alerts.py:148`, `routers/predictions.py:99`) vs endpoints returning bare arrays (`/api/alerts/active`, `/api/alerts/predictive`, `/api/alerts/reactive` — `alerts.py:188,226,263`; `/api/predictions/active` — `predictions.py:135`; `/api/correlations` — `correlations.py:166`; `/api/anomalies`; `/api/components/{id}/health-history|predictions|alerts`). The convention says "List endpoints return `{"data": [...]}`" with no exception list; the frontend already hedges with `result.data || result || []` (`src/services/api.ts:47,70,108`) — the smoking gun that two builders already diverged.

**Fix:** amend the Conventions table to enumerate the exempt endpoints, or add a blanket rule (every list endpoint wraps `{data:[]}`) and add the wrappers.

## M-2 — Prediction/alert TTB field aliasing is uncanonicalized

**Diverging pair:** `PredictionEngine` persists `time_to_breach_minutes` plus `time_to_breach_min`/`max` (`prediction_service.py:266-268`); alert payloads use `time_to_breach` (`main.py:42`); the generator emits `time_to_breach_minutes` (`prediction_generator.py:44`). The frontend maps *four* aliases — `timeToBreach ?? timeToBreachMinutes ?? time_to_breach_minutes ?? time_to_breach` (`api.ts:112`) — again proof of real divergence. The Conventions table has an IDs/Naming/Envelope/Error-shape row but no per-entity payload-field contract.

**Fix:** add a "payload shapes" row (or new AD "API Payload Contract") pinning prediction fields (`time_to_breach_minutes`, `time_to_breach_min`, `time_to_breach_max`, `confidence`, `prediction_type`) and alert fields (`time_to_breach`, `confidence`).

## M-3 — AD-08's alert_type vocabulary is actually {reactive, predictive, dynamic}

**Diverging pair:** AD-08 defines `reactive`/`predictive`; the runtime exposes dynamic alerts as `alert_type="dynamic"` (`alerts.py:97`) while persisting them as `"reactive"` (`alerts.py:35`); seed writes `reactive`/`predictive`. Consequence: `GET /api/alerts?alert_type=predictive` silently excludes the live dynamic alerts. Two alert-consumer builders can't agree on the type set.

**Fix:** amend AD-08 to bind the `alert_type` vocabulary to `{reactive, predictive}` and forbid `dynamic` in payloads (persist dynamic alerts under a real type, or expose a separate `origin` field).

## M-4 — No single threshold authority — three default dictionaries disagree

**Diverging pair:** `HealthCalculator.DEFAULT_THRESHOLDS` (`health_service.py:28-39`: latency critical 200), `metric_normalizer.get_default_thresholds` (`metric_normalizer.py:148-177`: latency critical 200, `lb_response_time` critical 1000), `prediction_service._get_default_threshold` (`prediction_service.py:246-251`: latency 200, error_rate 5), plus `Threshold` table rows which have no uniqueness constraint on `(component_type, metric_name)`. A builder of the "static threshold prediction level" (AD-01) and a builder of "health scoring" (AD-04) read different defaults for the same metric → the same value is breached for one engine and not the other.

**Fix:** declare the `Threshold` table (with the added unique constraint) plus `metric_normalizer` defaults as the single authority in AD-01; have health/prediction consume it. Medium because it is resolvable by amendment rather than a structural split.

---

# LOW

## L-1 — AD-05's "must block auto-actions on every path" has no enforcement point

`remediation_guard` has zero call sites in the codebase (grep confirms only its own module). A builder cannot tell which paths must call `prevent_auto_action` or how it is verified. **Fix:** amend AD-05 to name the enforcement seam (every service write path calls the guard; CI test greps for it) or mark it deferred until notification/escalation execution is wired.

## L-2 — `ComponentMetric.source` is ungoverned

Writers hardcode `"simulated"` (`metric_collector.py:103`, `metrics.py:90`) or `"system"` (`seed_service.py:130`) regardless of the component's actual source, while AD-06/Conventions govern only component tagging. **Fix:** extend the AD-06 tagging rule to metric rows.

## L-3 — `websocket.py:15` runs `eval(data)` on client input

Not covered by AD-02 (JSON over HTTP) or AD-07 (WS push). **Fix:** amend AD-02 or add a security row to Conventions forbidding eval and requiring structured WS messages.

## L-4 — Timestamp representation drift

Payloads mix FastAPI-serialized `datetime` objects (`alerts.py:143`), `isoformat()` strings (`websocket_manager.py:56`, `metric_normalizer.py:107`), and `strftime` strings (`seed_service.py:216`). All are ISO-8601 UTC, so this is minor, but the Conventions "Timestamps" row should state "naive UTC only, ISO-8601, no local conversion" to stop drift when a service is extracted (H-3).

---

# Summary of required changes

| # | Change | Severity | Type |
| --- | --- | --- | --- |
| C-1 | Prediction contract: confidence semantics, prediction_type vocabulary, single writer, unavailable representation | Critical | Amend AD-01 / new AD |
| C-2 | Canonical alert status set {open,acknowledged,resolved}, forbid active/escalated; define dedup key (component_id+metric); Alert.metric in ER; reactive carries no ttb/confidence | Critical | Amend AD-08 |
| H-1 | Mutation taxonomy + service registration + WS channel/message matrix | High | Amend AD-07 |
| H-2 | Component id namespacing + canonical source vocabulary + single tagging owner | High | New AD-10 / amend AD-06 |
| H-3 | Entity write-ownership matrix + single adapter registry; extraction gated on ownership | High | Amend AD-09 / new AD |
| M-1 | Envelope rule exhaustive | Medium | Conventions |
| M-2 | Payload field contract (TTB names) | Medium | Conventions / new AD |
| M-3 | alert_type vocabulary {reactive,predictive} | Medium | Amend AD-08 |
| M-4 | Single threshold authority | Medium | Amend AD-01 |
| L-1..L-4 | Guard enforcement point, metric source, WS eval, timestamp note | Low | Amend AD-05 / AD-02 / Conventions |