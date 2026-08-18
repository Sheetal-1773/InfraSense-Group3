# InfraSense - Health Analytics Platform

<p align="center">
  <img src="https://img.shields.io/badge/React-18-blue" alt="React">
  <img src="https://img.shields.io/badge/TypeScript-5-blue" alt="TypeScript">
  <img src="https://img.shields.io/badge/FastAPI-Python-green" alt="FastAPI">
  <img src="https://img.shields.io/badge/Prometheus-2.44-orange" alt="Prometheus">
  <img src="https://img.shields.io/badge/PostgreSQL-16-blue" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Docker-24-blue" alt="Docker">
</p>

## What is InfraSense?

InfraSense is an **IT early warning system** that predicts infrastructure failures before they happen. It provides:

- **Health Scores (0-100)** - Composite health metric per component
- **Time-to-Breach Predictions** - Predicted time until threshold crossing with confidence intervals
- **Explainable AI** - Clear reasoning: "91% confidence because CPU increased 18% over 2 hours..."
- **Blast Radius Analysis** - What else will be affected when this fails
- **Correlation Engine** - Links related issues across infrastructure layers
- **Recommended Actions** - Specific next steps with runbook integration

---

## Quick Start

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Docker | 24+ | Container runtime |
| Docker Compose | 2+ | Container orchestration |
| Node.js | 18+ | Frontend runtime |
| Python | 3.10+ | Backend runtime |

### Start Everything with One Command

```bash
cd health-analytics-platform
docker-compose up -d
```

### Access the Application

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:5173 | Main dashboard |
| **Backend API** | http://localhost:8000 | FastAPI server |
| **Prometheus** | http://localhost:9090 | Metrics collector |
| **API Docs** | http://localhost:8000/docs | API documentation |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│  React + TypeScript + Tailwind CSS + React Query            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │Dashboard │  │Components│  │ Alerts   │  │Correlations│   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                          │ HTTP
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                        BACKEND                               │
│                   FastAPI + SQLAlchemy                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              /api/components endpoint                 │   │
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
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    MONITORING STACK                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │Prometheus  │  │Node        │  │cAdvisor    │            │
│  │            │  │Exporter    │  │            │            │
│  └────────────┘  └────────────┘  └────────────┘            │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │PostgreSQL  │  │Blackbox    │  │Application │            │
│  │            │  │Exporter    │  │Services    │            │
│  └────────────┘  └────────────┘  └────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
health-analytics-platform/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── routers/           # API endpoints
│   │   │   ├── components.py  # Components CRUD
│   │   │   ├── alerts.py      # Alerts management
│   │   │   ├── predictions.py # Predictions API
│   │   │   └── correlations.py # Correlations API
│   │   ├── services/          # Business logic
│   │   │   ├── data_source_manager.py
│   │   │   ├── data_sources/
│   │   │   │   ├── base.py
│   │   │   │   ├── local_adapter.py
│   │   │   │   ├── simulator_adapter.py
│   │   │   │   ├── prometheus_adapter.py
│   │   │   │   └── solarwinds_mock.py
│   │   │   ├── alert_generator.py
│   │   │   ├── correlation_engine.py
│   │   │   └── metric_collector.py
│   │   ├── models/            # Database models
│   │   └── main.py            # App entry point
│   └── requirements.txt
│
├── src/                        # React frontend
│   ├── pages/
│   │   ├── Dashboard.tsx      # Main dashboard
│   │   ├── Components.tsx     # Component list
│   │   ├── Alerts.tsx         # Alert list
│   │   ├── Correlations.tsx   # Correlation view
│   │   ├── Predictions.tsx    # Predictions view
│   │   └── Settings.tsx       # Settings page
│   ├── components/            # Reusable components
│   ├── hooks/                 # React Query hooks
│   ├── services/              # API client
│   ├── types/                 # TypeScript types
│   └── App.tsx                # App entry point
│
├── monitoring/                 # Monitoring config
│   ├── docker-compose.yml     # Monitoring stack
│   ├── prometheus.yml         # Prometheus config
│   ├── blackbox.yml           # Blackbox config
│   └── alert.rules.yml        # Alert rules
│
├── docker-compose.yml          # Main orchestration
├── package.json                # Frontend dependencies
└── README.md                   # This file
```

---

## Features

### 1. Dashboard
- Overall system health overview
- Active alerts summary
- Health score cards
- Health trend charts

### 2. Components
- Grid/List view of all infrastructure components
- Filter by: Status, Category, Source
- Sort by: Name, Health, Last Updated
- Search functionality
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

## Data Sources

The platform supports multiple data sources:

| Source | Description | Metrics |
|--------|-------------|---------|
| **Local** | Local infrastructure | CPU, Memory, Disk, Network |
| **Simulator** | Synthetic test data | Generated metrics |
| **Prometheus** | Real-time metrics | From Prometheus exporters |
| **Mock SolarWinds** | Enterprise tool simulation | Simulated enterprise data |

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
| Lucide React | Icons |

### Backend
| Technology | Purpose |
|------------|---------|
| Python 3.10+ | Runtime |
| FastAPI | Web framework |
| SQLAlchemy | ORM |
| Pydantic | Validation |
| Uvicorn | ASGI server |

### Database & Monitoring
| Technology | Purpose |
|------------|---------|
| PostgreSQL | Main database |
| TimescaleDB | Time-series extension |
| Prometheus | Metrics collection |
| Node Exporter | Server metrics |
| cAdvisor | Container metrics |

---

## Configuration

### Environment Variables

**Backend** (`backend/.env`):
```env
DATABASE_URL=postgresql://infrasense:infrasense@postgres:5432/infrasense
DATA_MODE=prometheus
CLOUD_PROVIDER=local
SIMULATOR_ENABLED=true
PROMETHEUS_URL=http://prometheus:9090
```

**Frontend** (`.env`):
```env
VITE_API_URL=http://localhost:8000
```

---

## Development

### Running Locally

**1. Start the database and monitoring:**
```bash
docker-compose up -d postgres prometheus
```

**2. Start the backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**3. Start the frontend:**
```bash
npm install
npm run dev
```

### Building for Production

```bash
# Frontend
npm run build

# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/components` | GET | List all components |
| `/api/components/{id}` | GET | Get component details |
| `/api/alerts` | GET | List all alerts |
| `/api/alerts/{id}/acknowledge` | POST | Acknowledge alert |
| `/api/predictions` | GET | List predictions |
| `/api/correlations` | GET | List correlations |
| `/api/health` | GET | Health check |

---

## Troubleshooting

### Common Issues

**1. Prometheus not collecting metrics**
```bash
# Check Prometheus targets
curl http://localhost:9090/targets

# Check Prometheus logs
docker logs prometheus
```

**2. Backend not connecting to database**
```bash
# Check database is running
docker ps | grep postgres

# Check database logs
docker logs postgres
```

**3. Frontend not connecting to backend**
```bash
# Check backend is running
curl http://localhost:8000/api/health

# Check CORS settings in backend
```

---

## License

MIT License - See LICENSE file for details.

---

## Support

For issues or questions, please open an issue on GitHub.