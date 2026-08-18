---
title: "REVIEWER GATE — Technology Currency Review"
reviewer: "Technology-Currency Reviewer"
reviewed: "ARCHITECTURE-SPINE.md v2.1 (re-distilled 2026-08-17)"
date: "2026-08-17"
scope: "## Stack table, Structural Seed, Deferred claims vs. pinned code in health-analytics-platform/"
source-of-truth: "backend/requirements.txt, package.json, package-lock.json, docker-compose.yml, applications/requirements.txt, Dockerfiles (root, backend, applications)"
---

# Technology Currency Review — InfraSense Health Analytics Platform Spine

## Verdict

**CONDITIONAL PASS.** Every version the spine's `## Stack` table lists matches the actually-pinned code exactly — no version is invented, drifted, or phantom. The spine also correctly keeps OpenTelemetry, Prometheus, Kafka, Kubernetes, Grafana, and scikit-learn/pandas as Deferred and never implies they are live. The condition: the spine ratifies a small set of stale/EOL pins that predate the 2026-08-17 review date — most importantly the **Node 20 base image (EOL 2026-04-30)** and the **unpinned `timescale/timescaledb:latest-pg16` image tag** — plus backend pins (FastAPI 0.109, Uvicorn 0.27) that are ~2.5 years behind current. These do not make the spine factually wrong; they make it a ratified snapshot of a codebase whose own dependency currency needs attention. Fix the High item before next release; schedule the Medium items.

---

## Task 1 — Stack table vs. actual pinned code

Source of truth: `backend/requirements.txt` (exact pins), `package-lock.json` (resolved versions for the caret ranges in `package.json`), `docker-compose.yml`, `applications/requirements.txt`, `Dockerfile`s.

| Spine entry | Code pin (source) | Match |
| --- | --- | --- |
| Python 3.11 | `python:3.11-slim` (backend/Dockerfile; applications/*/Dockerfile) | ✅ Exact |
| FastAPI 0.109 | `fastapi==0.109.0` (requirements.txt) | ✅ Exact |
| Uvicorn 0.27 | `uvicorn==0.27.0` | ✅ Exact |
| SQLAlchemy 2.0.25 | `sqlalchemy==2.0.25` | ✅ Exact |
| Pydantic 2.5 | `pydantic==2.5.3` | ✅ Exact |
| NumPy 1.26 | `numpy==1.26.3` | ✅ Exact |
| TimescaleDB / PostgreSQL pg16 | `timescale/timescaledb:latest-pg16` (docker-compose.yml) | ⚠️ Version "pg16" matches, but the image tag is a floating `latest-pg16` — no TimescaleDB 2.x version is pinned (see High/Medium findings) |
| — SQLite dev default | `sqlite:///./infrasense.db` default in `backend/app/models/database.py`; sqlite in `backend/tests/conftest.py` | ✅ Confirmed |
| React 18.3 | `react@18.3.1`, `react-dom@18.3.1` (package-lock.json) | ✅ Exact |
| Vite 8.2 | `vite@8.2.1` resolved (`^8.2.0`) | ✅ Exact |
| TypeScript 5.9 | `typescript@5.9.3` resolved | ✅ Exact |
| React Router 7.18 | `react-router-dom@7.18.2` resolved (`^7.18.2`) | ✅ Exact |
| Recharts 3.10 | `recharts@3.10.1` resolved | ✅ Exact |
| TanStack React Query 5.101 | `@tanstack/react-query@5.101.4` resolved | ✅ Exact |
| Tailwind CSS 4.3 | `tailwindcss@4.3.3` resolved | ✅ Exact |
| Node (frontend image) 20-alpine | `node:20-alpine` (root Dockerfile) | ✅ Exact — but EOL (see High finding) |
| Demo apps (customer/payment/auth) Flask | `flask==3.0.0` (applications/requirements.txt); `Flask` imported in all three app.py | ✅ Confirmed (spine claims no version — correct, since it pins 3.0.0) |

**Result: zero version discrepancies.** The spine lists nothing the code does not pin, and every listed version matches the pin. Notably `@vitejs/plugin-react@6.0.x`, `vitest@4.1.x`, `oxlint@1.75.x`, `playwright@1.62.x`, `lucide-react@1.31.x` are in the lockfile but correctly not claimed in the spine's headline Stack table (acceptable summarization).

Secondary deps present in code but omitted from the Stack table (acceptable, but should be acknowledged somewhere in the spine for completeness): `asyncpg==0.29.0`, `psycopg2-binary==2.9.9`, `pydantic-settings==2.1.0`, `python-dotenv==1.0.0`, `httpx==0.26.0`, `websockets>=12.0`, `requests>=2.31.0`, `psutil>=5.9.0`, `pandas==2.1.4`, `scikit-learn==1.4.0`. `pandas`/`scikit-learn` are correctly surfaced in the Deferred table.

---

## Task 2 — Technology currency as of 2026-08-17 (web-verified)

### Confirmed current / fit for purpose (no action)
- **Vite 8.2** — current line (`vite@8.2` receives regular patches; Vite 8 shipped Mar 2026 with the Rolldown bundler). ✅
- **Recharts 3.10** — `recharts@3.10.1` (2026-07-25) is the latest. ✅
- **Tailwind CSS 4.3** — `tailwindcss@4.3.3` (2026-07-16) is the latest; 4.3 is the supported line. ✅
- **TanStack React Query 5.101** — `@tanstack/react-query@5.101.4` is the latest. ✅
- **TimescaleDB on PostgreSQL 16** — TimescaleDB 2.29.x (2026-07) supports PG 16/17/18; PG 15 support removed in 2.29. **PG 16 is fully supported** and is a supported PostgreSQL major (security support well past 2026). Fit for purpose. The concern is the *tag*, not the major (see findings). ✅ (with caveat)
- **Python 3.11** — still within its security-support window (EOL Oct 2027). ✅ (Low note below)

### Findings (see Findings section for details)
- **Node 20 (frontend image)** — **EOL since 2026-04-30.** No security patches. This is the one genuine currency failure in the ratified stack.
- **FastAPI 0.109** — pinned 2024-01; current is **0.141.x (2026-07)**. ~2.5 years, ~30 minor releases behind. Not EOL, but materially stale.
- **Uvicorn 0.27** — pinned 2023; current is 0.3x. Same class as FastAPI.
- **React 18.3** — current is **19.2.x**; 18.x is on the *maintenance* track (not EOL, per React's version tracker: 5 supported versions, 0 EOL). Plausibly outdated, not superseded. React 18.3 was explicitly published as the bridge release to React 19.
- **react-router-dom 7.18** — current *for the v7 line*, and v7 still receives security updates. **But React Router v8 shipped 2026-06 and removes the `react-router-dom` package entirely** (switch to `react-router` + `react-router/dom`). v6/Remix v2 are EOL. So the package name is on a sunset path, though the pinned version is supported today.
- **TypeScript 5.9** — TS **6.0.x** is current (6.0.3); 5.9.3 is the last 5.9 patch and remains maintained. One major behind.
- **Flask 3.0.0 (demo apps)** — pinned 2023-11; current is 3.1.x. Spine makes no version claim, so not a spine error, but the demo apps pin is stale.

---

## Task 3 — No phantom "live" technology

Confirmed: the spine never implies that OpenTelemetry, Prometheus, Kafka, Kubernetes, Grafana, or the ML stack (scikit-learn/pandas) are live.

- AD-04: *"Real monitoring tools (Datadog, Dynatrace, Splunk, Prometheus) are not wired today."* ✅ accurate — no such deps/config in code.
- AD-09: *"Kubernetes, Kafka, and cloud providers are not part of the topology today."* ✅ accurate — compose files are plain docker-compose.
- Deferred table rows for OTel/OTLP, Prometheus remote-write, Kafka, Kubernetes, Grafana datasource, and ML (scikit-learn/pandas, "Declared in requirements, unused") match code reality. ✅
- AD-03 uses *"sidecar/daemonset/agent"* as a future conditional only — aspirational wording, no live claim. ⚠️ Low note: terminology could be misread as implying k8s; consider rewording to "out-of-process collector/agent."

Two inconsistencies worth recording (both Low):
1. **Structural Seed System Context diagram draws `WEBHOOK` and `EMAIL` as live consumers** (`API --> WEBHOOK ; API --> EMAIL`), but the Deferred table states escalation/email/webhook modules are *implemented but not invoked at runtime*. The diagram overstates today's reality.
2. `applications/requirements.txt` declares `grpcio==1.60.0` and `protobuf==4.25.1`, but no demo app imports them (grep confirms zero `import grpc`). AD-02's "gRPC is not used today" holds at runtime, but the demo stack carries declared-but-unused gRPC deps that are unacknowledged anywhere in the spine.

---

## Findings (tiered)

### 🔴 High

**H1 — Node 20 base image is End-of-Life.**
- Technology: Node.js (frontend Dockerfile base image).
- Claim: Spine Stack row "Node (frontend image) — 20-alpine", and root `Dockerfile: FROM node:20-alpine`.
- Reality: Node.js 20 (Iron) reached EOL **2026-04-30** — ~3.5 months before this review. No security patches or CVE fixes will ever ship for it; CVEs disclosed after EOL are unfixed. `node:20-alpine` is an unpatched, static artifact.
- Recommended fix: Bump the frontend image to a supported LTS — `node:22-alpine` (maintenance LTS through 2027-04-30) or `node:24-alpine` (active LTS). Verify the SPA build (`vite@8.2`, `@vitejs/plugin-react@6`) and `npm run build` on the new runtime; update the spine Stack row to match the new major.

### 🟠 Medium

**M1 — `timescale/timescaledb:latest-pg16` is a floating tag; no TimescaleDB 2.x version is pinned.**
- Technology: TimescaleDB / PostgreSQL.
- Claim: Spine lists "TimescaleDB / PostgreSQL — pg16 (compose)" with no TimescaleDB version.
- Reality: `docker-compose.yml` uses `image: timescale/timescaledb:latest-pg16`. `latest-pg16` drifts forward on every image rebuild and can break the stack without a code change (the project itself just went through a major where TimescaleDB 2.29 dropped PG15 and added PG16/17/18 image variants). PG16 itself is fully supported by TimescaleDB 2.29.x and is a supported PostgreSQL major — the choice of major is fine; the tag is non-reproducible.
- Recommended fix: Pin a concrete image, e.g. `timescale/timescaledb:2.29.1-pg16` (or the current minor at rebuild time), and record the TimescaleDB 2.x version in the spine Stack row (e.g. "TimescaleDB 2.29 / PostgreSQL 16").

**M2 — Backend pins ~2.5 years behind current: FastAPI 0.109 / Uvicorn 0.27.**
- Technology: FastAPI, Uvicorn.
- Claim: Spine Stack rows "FastAPI 0.109", "Uvicorn 0.27"; code pins `fastapi==0.109.0`, `uvicorn==0.27.0` (2023–2024).
- Reality: As of 2026-08, FastAPI is at **0.141.x** (released 2026-07) and Uvicorn at 0.3x. The pinned versions are ~30 FastAPI minors / ~2.5 years behind, missing security fixes, performance work, and Pydantic v2 API improvements. Neither is EOL, and the spine is accurate to the code — this is a dependency-hygiene issue the spine silently ratifies.
- Recommended fix: Schedule a backend dependency refresh (FastAPI + Uvicorn + Pydantic as a compatible set, re-run the backend test suite — `httpx` + `pytest` cover it). Update the spine Stack rows to the new pins. At minimum, add a note in the spine's Deferred/Open Questions so the stale pin is a tracked decision rather than an accident.

**M3 — React 18.3 is on the maintenance track while 19.2 is current.**
- Technology: React / React DOM.
- Claim: Spine "React 18.3"; code pins `react@18.3.1`, `react-dom@18.3.1` (2024-04).
- Reality: Current stable is **React 19.2.x** (19.2.7, 2026-06). React 18.x is maintenance (still supported, not EOL), and 18.3 was deliberately published as the bridge release to 19. Staying on 18.3 is viable but the project is now two majors of upstream ecosystem movement behind (e.g. newer libraries increasingly ship React 19-first). React Router 7 and Recharts 3 both support React 19, so the migration path is low-risk.
- Recommended fix: Plan a React 19 migration (the official 18→19 codemods); move `@types/react`/`@types/react-dom` to 19 in the same step. Until then, keep the spine honest with a Deferred note "React 19 upgrade (tracked)".

### 🟡 Low

**L1 — `react-router-dom` package name is removed in React Router v8.**
- Technology: React Router.
- Claim: Spine "React Router 7.18"; code pins `react-router-dom@7.18.2`.
- Reality: 7.18.2 is the latest v7 and v7 still receives security updates (v6/Remix v2 are EOL as of v8). But v8 (2026-06) drops the `react-router-dom` package — imports must move to `react-router`/`react-router/dom`. The pinned version is correct today; the package name has a sunset.
- Recommended fix: No action now. Add a Deferred note: "React Router v8 upgrade — replace `react-router-dom` imports with `react-router` / `react-router/dom`."

**L2 — TypeScript 5.9 is one major behind 6.0.**
- Technology: TypeScript.
- Claim: Spine "TypeScript 5.9"; code pins `typescript@5.9.3` (last 5.9 patch).
- Reality: TS **6.0.x** is current (6.0.3, 2026-06). 5.9.3 remains maintained and is a reasonable pin; nothing is wrong today.
- Recommended fix: Fold a TS 6.0 bump into the next frontend toolchain refresh; verify `tsc -b` and the Vitest/oxlint pipeline.

**L3 — Flask 3.0.0 demo apps pin is stale.**
- Technology: Flask (demo customer/payment/auth apps).
- Claim: Spine lists demo apps as "Flask" (no version — correct, because the code does pin one).
- Reality: `flask==3.0.0` (2023-11); current is 3.1.x. The demo apps are monitored targets, so currency matters less, but the pin is 2.5 years old.
- Recommended fix: Bump to `flask==3.1.x`; if the spine ever states a demo-app version, use that. Otherwise no spine change needed.

**L4 — Structural Seed diagram implies live Email/Webhook consumers that are actually deferred.**
- Technology: notification delivery.
- Claim: System Context diagram draws `API --> WEBHOOK` and `API --> EMAIL` as active arrows.
- Reality: Deferred table correctly says escalation/email/webhook modules are "implemented but not invoked at runtime." The diagram overstates live delivery.
- Recommended fix: Render EMAIL/WEBHOOK with dashed "deferred" styling, or annotate the arrows as "planned," to match AD-07's two-write-path reality.

**L5 — Declared-but-unused `grpcio`/`protobuf` in demo apps.**
- Technology: gRPC tooling.
- Claim: AD-02 "gRPC is not used today" — true at runtime (no `import grpc` anywhere).
- Reality: `applications/requirements.txt` pins `grpcio==1.60.0` and `protobuf==4.25.1`, which are dead weight and unacknowledged in the spine.
- Recommended fix: Remove the unused pins from the demo apps requirements, or add a one-line Deferred note if they are a deliberate precursor. Spine itself needs no change.

**L6 — Python 3.11 approaching security-window end (Oct 2027); ASP-era wording "daemonset" in AD-03.**
- Technology: Python runtime; AD-03 wording.
- Claim: Spine "Python 3.11"; AD-03 references "sidecar/daemonset/agent."
- Reality: 3.11 is fine through 2027-10, so no urgency; "daemonset" is Kubernetes vocabulary used in a future conditional only and could be misread as implying k8s is present.
- Recommended fix: No immediate action. Consider `python:3.12-slim` or `3.13-slim` at the next backend rebuild; reword AD-03 to "out-of-process collector/agent" to avoid k8s vocabulary.

---

## Bottom line

The spine is **factually accurate against the code** on every version it claims and **disciplined** about what is Deferred vs. live — the re-distillation did its job. What the review surfaces is that the spine now *ratifies* a dependency set whose currency is drifting: one EOL runtime (Node 20), a floating TimescaleDB tag, and backend pins ~2.5 years stale. Approve the spine as-is for architecture purposes; attach H1 and M1–M3 as tracked follow-ups so the ratified snapshot does not silently become the long-term posture.
