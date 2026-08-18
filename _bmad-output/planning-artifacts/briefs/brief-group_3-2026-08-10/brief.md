---
title: Health Analytics Platform
status: complete
created: 2026-08-10
updated: 2026-08-18
---

# Product Brief: Health Analytics Platform (InfraSense)

## Executive Summary

The Health Analytics Platform is an **IT early warning system** that predicts infrastructure failures before they happen — not just monitors current state. Built as an overlay intelligence layer on existing monitoring tools, it delivers **actionable early warnings** with explainable predictions, business impact, and recommended actions.

**Core promise:** Predict the problem, alert early enough to prevent it, explain why it will happen, show what it will affect, and recommend what to do.

---

## What is InfraSense?

InfraSense is a full-stack monitoring and analytics platform that provides:

| Feature | Description |
|---------|-------------|
| **Health Score (0-100)** | Composite health metric per component |
| **Time-to-Breach** | Predicted time until threshold crossing with confidence interval |
| **Explainability** | Clear reasoning: "91% confidence because CPU increased 18% over 2 hours..." |
| **Blast Radius** | What else will be affected when this fails |
| **Correlation** | Links related issues across infrastructure layers |
| **Recommended Actions** | Specific next steps with runbook integration |

---

## Current Status: ✅ COMPLETE

The platform has been fully implemented with all core features working:

- ✅ Dashboard with health overview
- ✅ Components page with filtering (Local, Simulated, Prometheus)
- ✅ Real-time metrics (CPU, Memory, Disk)
- ✅ Alert generation and display
- ✅ Correlation detection
- ✅ Predictions engine
- ✅ Docker Compose deployment

---

## Technology Stack

### Frontend
| Technology | Purpose |
|------------|---------|
| React 18 | UI framework |
| TypeScript | Type safety |
| Tailwind CSS | Styling |
| Vite | Build tool |
| React Query | Data fetching |
| React Router | Navigation |

### Backend
| Technology | Purpose |
|------------|---------|
| Python 3.10+ | Runtime |
| FastAPI | Web framework |
| SQLAlchemy | ORM |
| Pydantic | Validation |

### Database & Monitoring
| Technology | Purpose |
|------------|---------|
| PostgreSQL | Main database |
| TimescaleDB | Time-series |
| Prometheus | Metrics collection |
| Node Exporter | Server metrics |
| Docker | Containerization |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│  React + TypeScript + Tailwind CSS + React Query            │
│  http://localhost:5173                                      │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTP
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                        BACKEND                               │
│  FastAPI + SQLAlchemy + Pydantic                            │
│  http://localhost:8000                                      │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                   API Endpoints                       │   │
│  │  /api/components  /api/alerts  /api/predictions      │   │
│  │  /api/correlations  /api/health                      │   │
│  └────────────────────────┬─────────────────────────────┘   │
│                           │                                   │
│  ┌────────────────────────▼─────────────────────────────┐   │
│  │           Data Source Manager                         │   │
│  │  (Local, Simulator, Prometheus, Mock adapters)        │   │
│  └────────────────────────┬─────────────────────────────┘   │
│                           │                                   │
│  ┌────────────┬───────────┼───────────┬────────────┐        │
│  ▼            ▼           ▼           ▼            ▼        │
│ ┌──────┐ ┌────────┐ ┌──────────┐ ┌─────────┐ ┌───────┐     │
│ │Local │ │Simulator│ │Prometheus│ │  Mock   │ │  DB   │     │
│ │Adapter│ │Adapter │ │ Adapter  │ │ Adapter │ │(Postgres)│    │
│ └──────┘ └────────┘ └──────────┘ └─────────┘ └───────┘     │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    MONITORING STACK                          │
│  Prometheus + Node Exporter + cAdvisor + PostgreSQL         │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Sources

The platform supports multiple data sources that can be filtered in the Components page:

| Source | Description | Filter Value |
|--------|-------------|--------------|
| **Local** | Local infrastructure | `local` |
| **Simulator** | Synthetic test data | `simulated` |
| **Prometheus** | Real-time metrics | `prometheus` |
| **Mock SolarWinds** | Enterprise tool simulation | `mock` |

---

## Quick Start

```bash
# Clone and navigate to project
cd health-analytics-platform

# Start everything with Docker Compose
docker-compose up -d

# Access the application
# Frontend: http://localhost:5173
# Backend:  http://localhost:8000
# Prometheus: http://localhost:9090
```

---

## Key Features Implemented

### 1. Dashboard
- Overall system health overview
- Active alerts summary
- Health score cards
- Health trend charts

### 2. Components Page
- Grid/List view toggle
- Filter by Source (All, Local, Simulated, Prometheus)
- Filter by Status (All, Healthy, Warning, Critical)
- Filter by Category (Network, Applications, Databases, Servers)
- Sort by Name, Health, Last Updated
- Search functionality
- Pagination
- Component detail modal with metrics

### 3. Alerts
- Real-time alert generation
- Alert severity levels (critical, warning, info)
- Alert acknowledgment
- Time-to-breach predictions

### 4. Correlations
- Incident analysis
- Dependency chain visualization
- Contributing factors display
- Recommended actions

### 5. Predictions
- Time-to-breach predictions
- Confidence intervals
- Historical pattern matching
- Prediction explanation

### 6. Settings
- Data source configuration
- Threshold configuration
- Alert preferences

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/components` | GET | List all components (?source= filter supported) |
| `/api/components/{id}` | GET | Get component details |
| `/api/alerts` | GET | List all alerts |
| `/api/alerts/{id}/acknowledge` | POST | Acknowledge alert |
| `/api/alerts/{id}/resolve` | POST | Resolve alert |
| `/api/predictions` | GET | List predictions |
| `/api/correlations` | GET | List correlations |
| `/api/health` | GET | Health check |

---

## Success Criteria Met

| Criteria | Status |
|----------|--------|
| Real-time metrics collection | ✅ |
| Health score calculation | ✅ |
| Alert generation | ✅ |
| Correlation detection | ✅ |
| Prediction engine | ✅ |
| Source filtering | ✅ |
| Docker Compose deployment | ✅ |

---

## Target Users

- **NOC Teams** — Need early warning before customers call
- **IT Operations** — Want proactive, not reactive, monitoring
- **SREs** — Need confidence intervals and clear recommendations
- **Infrastructure Teams** — Want correlation across layers
- **Application Owners** — Need business impact context

---

## Target Market

- **Organization size:** Mid-market to Enterprise
- **Industries:** Financial services, healthcare, telecom, critical infrastructure
- **Environment:** Multi-cloud or hybrid infrastructure with existing monitoring investments

---

## Vision

InfraSense becomes the **predictive layer** that every IT operations team relies on — the system that tells you what's about to break before it breaks.

---

## License

MIT License