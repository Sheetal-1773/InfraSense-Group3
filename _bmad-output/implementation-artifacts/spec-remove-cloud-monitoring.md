---
title: 'Remove Cloud (Azure/AWS) Monitoring; Keep Local + Simulated Only'
type: 'refactor'
created: '2026-08-16'
status: 'complete'
updated: '2026-08-18'
baseline_commit: 0f2e9e8da8d86b4648c9e765a0078a038dc35872
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The monitoring stack currently provisions and consumes cloud infrastructure — Azure setup scripts, AWS setup scripts, Prometheus `azure_sd_configs`, Azure-specific metric queries, and `CLOUD_PROVIDER=azure` defaults — to source monitored components. The team wants monitoring to depend on no cloud provider at all: it must run entirely on **local** and **simulated** data sources.

**Approach:** Delete the Azure and AWS provisioning/verification artifacts, remove the Azure Prometheus scrape jobs and Azure metric queries, and change every provider default/fallback across configs, backend adapters, and frontend from `azure`/`aws` to `local`.

## Boundaries & Constraints

**Always:**
- Delete `infrastructure/azure_setup.py`, `infrastructure/aws_setup.py`, `scripts/verify_azure_e2e.py`.
- Every default/fallback for provider metadata must become `local` (never azure/aws).
- Remove Azure/AWS environment/secret references from `.env.example` and `docker-compose.yml`.
- Prometheus config must still be valid YAML and contain only local/non-cloud scrape jobs; no dangling `${AZURE_*}` or `${AWS_*}` placeholders.
- Keep the local, simulator, and mock (solarwinds) adapters fully functional and discoverable.

**Ask First:**
- None expected. If an Azure/AWS reference is found that this spec does not list, HALT and ask.

**Never:**
- Do not add new cloud provider code, configs, or metric queries.
- Do not remove the local/simulator/mock adapters or their generated data.
- Do not rename public API response keys (`cloud_provider` remains a field; its value becomes `local`).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | `docker compose up -d`, backend `DATA_MODE=mock` | Backend discovers local + simulator + mock components; `cloud_provider` reports `local`; Prometheus scrapes only local jobs | N/A |
| MISSING_ENV | No `CLOUD_PROVIDER` set anywhere | All code falls back to `local`, never azure/aws | N/A |
| SUMMARY_API | `GET /api/components/infrastructure/summary` | `by_provider` contains only `local`/`simulated`/`prometheus`; no `azure` key | azure branch removed |
| CONFIG_VALIDITY | edited `prometheus.yml` | `prometheus --check-config` passes | all azure/aws jobs and env placeholders removed |

</frozen-after-approval>

## Code Map

- `health-analytics-platform/infrastructure/azure_setup.py` -- DELETE Azure provisioning script
- `health-analytics-platform/infrastructure/aws_setup.py` -- DELETE AWS provisioning script
- `health-analytics-platform/scripts/verify_azure_e2e.py` -- DELETE Azure E2E verifier (generic `verify_e2e.py` remains)
- `health-analytics-platform/prometheus.yml` -- remove `azure-vms`, `azure-postgres`, `azure-load-balancer` jobs; change global+job `cloud_provider` labels to `local`; keep `local-mock` and other local jobs
- `health-analytics-platform/docker-compose.yml` -- `CLOUD_PROVIDER=azure` → `local`
- `health-analytics-platform/.env.example` -- drop Azure credentials block
- `health-analytics-platform/backend/app/services/data_sources/base.py` -- `cloud_provider` default → `local`
- `health-analytics-platform/backend/app/services/data_source_manager.py` -- `CLOUD_PROVIDER` env default → `local`
- `health-analytics-platform/backend/app/services/data_sources/prometheus_adapter.py` -- `CLOUD_PROVIDER` env default → `local`
- `health-analytics-platform/backend/app/services/data_sources/otel_adapter.py` -- `CLOUD_PROVIDER` default → `local`; replace `azure_load_balancer_*` PromQL with generic `load_balancer_*` names
- `health-analytics-platform/backend/app/routers/components.py` -- `os.getenv("CLOUD_PROVIDER", "azure")` fallbacks → `local`; drop `azure` from `by_provider` dict and its branch
- `health-analytics-platform/src/pages/Components.tsx` -- remove `azure` from `SOURCE_MAPPING`, `SourceFilter`, and the filter `<option>`
- `health-analytics-platform/src/pages/Dashboard.tsx` -- remove `azure` from source-breakdown color mapping

## Tasks & Acceptance

**Execution:**
- [x] `infrastructure/azure_setup.py` -- delete file -- cloud provisioning no longer used
- [x] `infrastructure/aws_setup.py` -- delete file -- cloud provisioning no longer used
- [x] `scripts/verify_azure_e2e.py` -- delete file -- Azure-specific verification obsolete (`verify_e2e.py` covers the local pipeline)
- [x] `prometheus.yml` -- remove three Azure jobs and change `cloud_provider` label to `local` -- no cloud scrape targets remain
- [x] `docker-compose.yml` -- `CLOUD_PROVIDER=local` -- set provider to local default
- [x] `.env.example` -- remove Azure credentials block -- no cloud secrets shipped in docs
- [x] `backend/app/services/data_sources/base.py` -- default `cloud_provider` returns `local` -- provider neutrality
- [x] `backend/app/services/data_source_manager.py` -- `os.getenv("CLOUD_PROVIDER", "local")` -- fallback is local
- [x] `backend/app/services/data_sources/prometheus_adapter.py` -- `os.getenv("CLOUD_PROVIDER", "local")` -- fallback is local
- [x] `backend/app/services/data_sources/otel_adapter.py` -- provider default `local`; rename `azure_load_balancer_*` metric names to `load_balancer_*` -- no Azure metric coupling
- [x] `backend/app/routers/components.py` -- `"local"` fallbacks; `by_provider = {"local": 0, "simulated": 0, "prometheus": 0}`; drop `source == "azure"` branch -- summaries never show azure
- [x] `src/pages/Components.tsx` -- remove azure from `SOURCE_MAPPING`, `SourceFilter`, and dropdown -- UI offers only local/simulated sources
- [x] `src/pages/Dashboard.tsx` -- remove azure color branch in `sourceBreakdown` -- dashboard shows only live sources

**Acceptance Criteria:**
- Given no `CLOUD_PROVIDER` env is set, when the backend initializes, then `cloud_provider`/provider values resolve to `local` everywhere.
- Given the backend is running with mock data mode, when `GET /api/components/infrastructure/summary` is called, then `by_provider` contains no `azure` (and no `aws`) key and `cloud_provider` equals `local`.
- Given `GET /api/components/discover`, when a component has no explicit provider, then `provider` defaults to `local`, never `azure`.
- Given `prometheus.yml` after the change, when run through Prometheus config validation, then config is valid and contains no `azure_sd_configs`, `azure-vms`, `azure-postgres`, `azure-load-balancer`, or `${AZURE_*}` references.
- Given the frontend, when the source filter is opened, then only `Local` and `Simulated` options exist (no `Azure`).
- Given the repo after the change, when searching for `azure|aws` (case-insensitive) in `health-analytics-platform` excluding `node_modules`/`dist`, then no cloud-monitoring references remain.

## Spec Change Log

- **2026-08-16 (human report: "dashboard not visible")** — Dashboard page failed to render: `useMemo` (`sourceBreakdown`) was called after the conditional early return for loading state, violating Rules-of-Hooks and causing a runtime crash. Amended: hoisted the `useMemo` above the `if (healthLoading || ...)` return so hook order is stable. Known-bad state avoided: blank/crashed dashboard. KEEP: `sourceBreakdown` must be computed unconditionally before any early return.

## Verification

**Commands:**
- `npm run build` -- expected: TypeScript compiles cleanly (frontend type changes valid)
- `npm run lint` -- expected: oxlint passes
- `prometheus --check-config` (or `docker compose exec prometheus prometheus --config.file=/etc/prometheus/prometheus.yml --check-config`) -- expected: config valid, no azure/aws jobs
- Python syntax check of edited backend files: `python -m py_compile` on the four edited files -- expected: no syntax errors

**Manual checks (if no CLI):**
- Grep `health-analytics-platform` (excluding `node_modules`, `dist`) for `azure`/`aws` case-insensitive -- expected: no cloud-monitoring hits remain