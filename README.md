# Claryo Dashboard

Real-time monitoring for industrial sensor data — **pressure, flow rate, and temperature** — sourced from Azure Data Explorer (ADX).

A FastAPI backend queries ADX over Kusto and exposes a small REST surface; a React frontend renders live dashboards, alerts, and CSV exports on top of it. Both halves deploy to Azure (Container Apps / App Service for the API, Static Web Apps for the UI) via the workflows in [`.github/workflows/`](.github/workflows/).

---

## Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
- [Running locally](#running-locally)
- [API reference](#api-reference)
- [Project structure](#project-structure)
- [Deployment](#deployment)
- [Security](#security)
- [License](#license)

## Features

- **Live sensor readings** polled from ADX and rendered as time-series charts
- **Per-metric dashboards** for temperature, pressure, and flow, plus a combined summary view
- **Threshold alerting** — `/sensors/check_alerts` flags readings outside configured bounds
- **CSV export** of any filtered query via `/export`
- **Summary endpoints** returning aggregates per metric for at-a-glance tiles

## Architecture

```
┌──────────────────┐        ┌────────────────────┐        ┌─────────────────┐
│  React frontend  │──REST─▶│  FastAPI backend   │──KQL──▶│  Azure Data     │
│  (Static Web App)│        │  (Container App)   │        │  Explorer (ADX) │
└──────────────────┘        └────────────────────┘        └─────────────────┘
        │                            │
   Recharts dashboards      Entra service principal auth
   Alerts · CSV export      (azure-kusto-data)
```

The backend authenticates to ADX with a Microsoft Entra application key (`KustoConnectionStringBuilder.with_aad_application_key_authentication`). CORS is restricted to the deployed Static Web App origin and `localhost:3000` for development.

## Prerequisites

| Component | Requirement |
|---|---|
| Backend | Python 3.11+ |
| Frontend | Node.js 18+ and npm (or yarn) |
| Data | An ADX cluster and database containing the sensor tables |
| Auth | An Entra service principal with **Database Viewer** on the ADX database |
| Optional | Docker, for the containerised backend |

## Configuration

Both halves read configuration from `.env` files that are **not** committed. Copy the provided examples and fill in your own values:

```bash
cp claryo-backend/.env.example claryo-backend/.env
cp claryo-frontend/.env.example claryo-frontend/.env
```

**`claryo-backend/.env`**

| Variable | Description |
|---|---|
| `KUSTO_CLUSTER` | ADX cluster URI, e.g. `https://<cluster>.<region>.kusto.windows.net` |
| `KUSTO_DB` | Database name (defaults to `claryoMVPDB`) |
| `APP_ID` | Entra application (client) ID |
| `APP_SECRET` | Entra client secret |
| `TENANT_ID` | Entra tenant ID |

Create the service principal with:

```bash
az ad sp create-for-rbac --name claryo-adx-reader
```

**`claryo-frontend/.env`**

| Variable | Description |
|---|---|
| `REACT_APP_API_URL` | Base URL of the backend API |

> ⚠️ `REACT_APP_*` values are inlined into the public JavaScript bundle at build time. Never put a secret in the frontend `.env`.

## Running locally

**Backend**

```bash
cd claryo-backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Interactive API docs are then served at <http://localhost:8000/docs>.

**Frontend**

```bash
cd claryo-frontend
npm install
npm start
```

The UI runs at <http://localhost:3000> and expects the API at whatever `REACT_APP_API_URL` points to.

**With Docker**

```bash
cd claryo-backend
docker compose up --build
```

## API reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `GET` | `/sensors/latest` | Most recent readings across all sensors |
| `GET` | `/sensors/average_pressure_latest` | Latest average pressure |
| `GET` | `/sensors/check_alerts` | Readings breaching configured thresholds |
| `GET` | `/sensors/temperature_summary` | Aggregated temperature statistics |
| `GET` | `/sensors/pressure_summary` | Aggregated pressure statistics |
| `GET` | `/sensors/flow_summary` | Aggregated flow-rate statistics |
| `GET` | `/export` | Streaming CSV export of the current query |

## Project structure

```
claryo-backend/
  main.py              FastAPI app, ADX client, all endpoints
  config.py            Environment-backed configuration
  requirements.txt
  Dockerfile
  docker-compose.yml
  tests/
claryo-frontend/
  src/
    pages/             Dashboard, Temperature, Pressure, Flow, CombinedSummary
    components/        Layout, Sidebar, TopBar, ChartCard, MetricTable,
                       AlertsPanel, FilterBar
    App.js
  public/
    staticwebapp.config.json
.github/workflows/     App Service and Static Web Apps deployment pipelines
```

## Deployment

Two GitHub Actions workflows handle deployment:

- `master_claryo-webapp.yml` — builds and deploys the FastAPI backend
- `azure-static-web-apps-*.yml` — builds and deploys the React frontend

Backend secrets should be supplied as **App Service / Container App application settings** (or, preferably, Key Vault references) rather than baked into the image.

## Security

- Secrets are read from the environment only; no credentials belong in the repository
- Prefer **managed identity** over a client secret for ADX access where the hosting platform supports it — it removes secret rotation entirely
- The ADX service principal should hold the least privilege that works, typically `Database Viewer`
- CORS origins are allow-listed explicitly in `main.py`; add new origins there rather than widening to `*`

## License

MIT — see [LICENSE](LICENSE).
