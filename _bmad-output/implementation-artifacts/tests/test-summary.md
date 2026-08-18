---
status: complete
updated: 2026-08-18
---

# Test Summary

**Project:** InfraSense Health Analytics Platform (`group_3`)
**Date:** 2026-08-18
**Status:** ALL TESTS PASSING
**Scope:** Backend API tests (pytest), frontend unit tests (Vitest + Testing Library), frontend E2E tests (Playwright)

## Test Results

| Suite | Framework | Files | Tests | Result |
|---|---|---|---|---|
| Backend API | pytest 9.1.1 | 7 | 54 | All passing |
| Frontend unit | Vitest 4.1.10 + Testing Library | 4 | 44 | All passing |
| Frontend E2E | Playwright (Chromium) | 5 | 19 | All passing |
| **Total** | | **16** | **117** | **All passing** |

## How to Run

```bash
# Backend API tests
cd backend
python -m pytest -q

# Frontend unit tests
npm run test

# Frontend E2E tests (starts its own mock backend on 8001 + dev server on 5174)
npx playwright test
```

## What Was Covered

### Backend API (`backend/tests/`)
- **test_health.py** — `/api/health` returns healthy status and correct data mode
- **test_components.py** — component CRUD, health scores, metrics, correlation references, detail
- **test_alerts.py** — alert list/filter, detail, acknowledge, resolve, manual generation
- **test_predictions.py** — prediction list, detail, accuracy, generation
- **test_metrics.py** — metric ingestion, dashboard metrics
- **test_simulator.py** — simulator enable/disable and component discovery
- **test_categories_correlations.py** — categories, correlations, topology, incidents

### Frontend Unit (`src/`)
- **format.test.ts** — number/percent/status/severity/health-bar formatting helpers (28 tests)
- **Badge.test.tsx** — variant classes and label rendering (5 tests)
- **Button.test.tsx** — variants, sizes, disabled state, click handling (6 tests)
- **HealthScoreCard.test.tsx** — score rendering and status logic (5 tests)

### Frontend E2E (`tests/e2e/`)
- **navigation.spec.ts** — header nav links and cross-page routing
- **dashboard.spec.ts** — key sections, Live indicator, predictive warnings, category overview
- **components.spec.ts** — filters, search, status filter, detail modal
- **alerts.spec.ts** — filters, table headers, severity filter, link to predictions
- **predictions.spec.ts** — page load, prediction list

## Bugs Found and Fixed During Testing

The backend tests exposed genuine application bugs that were fixed in `backend/app/routers/`:

1. **components.py** — used `m.current_value` which does not exist on `ComponentMetric`; corrected to `m.value`.
2. **metrics.py** — stray `@router.get("/metrics/health")` decorator attached to `validate_metric`; removed.
3. **correlations.py** — parameterized routes shadowed static routes; reordered `/topology`, `/incidents`, `/component/{id}/downstream|upstream`, `/{correlation_id}` to end of file. Fixed `comp.type` (column does not exist) to `comp.category.type` with environment fallback.
4. **alerts.py** — `/generate` was shadowed by `/{alert_id}`; moved earlier. Used non-existent `analyze_all_components`/`get_alert_summary`; replaced with `check_components` and inline summary.
5. **predictions.py** — `/accuracy` and `/generate` shadowed by `/{prediction_id}`; moved earlier. Duplicate `/accuracy` route removed. Used non-existent `analyze_all_components`/`get_prediction_summary`; replaced with `generate_predictions` and inline summary.

## Test Infrastructure Notes

- **Backend**: `conftest.py` sets mock mode env vars, creates a temp SQLite DB, seeds data via `run_full_seed`, overrides `get_db`, and disposes the engine after tests. The app lifespan is intentionally not run in tests to avoid background threads mutating the test DB.
- **Frontend**: Vitest configured in `vite.config.ts` (jsdom, `threads` pool to avoid worker timeouts on Node 24), setup file registers jest-dom matchers. Tests live alongside source in `src/`.
- **E2E**: `playwright.config.ts` declares two webServers — a self-contained mock backend (port 8001, SQLite, seed data) and a Vite dev server (port 5174, proxy to 8001). This isolates tests from any developer-run backend on port 8000. `VITE_API_PROXY` env var makes the Vite proxy target overridable.
