# Claryo Dashboard

Real-time monitoring for industrial sensor data — **pressure, flow rate, and temperature** — sourced from Azure Data Explorer (ADX).

A FastAPI backend queries ADX over Kusto and exposes a small REST surface; a React frontend renders live dashboards, alerts, and CSV exports on top of it. The whole stack is generic — **deploy it into your own Azure subscription with a single `azd up`** (App Service for the API, Static Web Apps for the UI, and an ADX cluster for the data). By default the backend authenticates to ADX with a **managed identity**, so there is no secret to manage.

---

## Contents

- [Features](#features)
- [Architecture](#architecture)
- [Deploy to your own subscription](#deploy-to-your-own-subscription)
- [Configuration](#configuration)
- [Running locally](#running-locally)
- [API reference](#api-reference)
- [Project structure](#project-structure)
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
│  (Static Web App)│        │   (App Service)    │        │  Explorer (ADX) │
└──────────────────┘        └────────────────────┘        └─────────────────┘
        │                            │
   Recharts dashboards      Managed identity by default
   Alerts · CSV export      (azure-kusto-data)
```

The backend authenticates to ADX using `DefaultAzureCredential` by default — a managed identity in Azure, or your `az login` session locally — so **no client secret is required**. Set `AUTH_MODE=app_key` to fall back to a Microsoft Entra service principal instead. CORS origins come from `ALLOWED_ORIGINS`; the deployment wires this to your Static Web App URL automatically.

## Deploy to your own subscription

The repository ships with an [Azure Developer CLI](https://aka.ms/azd) template. From a clone:

```bash
azd auth login
azd up
```

`azd up` provisions everything into a new resource group in **your** subscription and deploys both apps:

| Resource | Purpose |
|---|---|
| Azure Data Explorer cluster + database | Time-series store (`IoTDatabase`), with the `IoTSensorData` table created automatically |
| Linux App Service (Python) | The FastAPI backend, with a **system-assigned managed identity** granted `Database Viewer` on the ADX database |
| Static Web App | The React frontend |

No service principal or secret is created — the App Service's managed identity is what reads ADX. CORS and the frontend's API URL are wired from deployment outputs.

Infrastructure lives in [`infra/`](infra/) (Bicep) and is described by [`azure.yaml`](azure.yaml). The Static Web App region defaults to `westeurope`; override with `azd env set AZURE_STATIC_WEB_APP_LOCATION <region>` before `azd up`.

> **Seed data:** a fresh cluster is empty. Run the commands in [`scripts/setup-adx.kql`](scripts/setup-adx.kql) in the ADX query pane to add a few sample rows, or point `claryo-backend/tests/sensor_sim.py` at your cluster for continuous data.

### Bring your own resources (manual)

If you already have an ADX cluster, skip `azd` and just configure `.env` (below). Grant your identity `Database Viewer` on the database:

```bash
# For a managed identity or your own user, add a database principal:
# .add database <db> viewers ('aadapp=<app-or-mi-client-id>;<tenant-id>')
```

## Configuration

Both halves read configuration from `.env` files that are **not** committed. Copy the examples and fill in your own values:

```bash
cp claryo-backend/.env.example claryo-backend/.env
cp claryo-frontend/.env.example claryo-frontend/.env
```

**`claryo-backend/.env`**

| Variable | Description |
|---|---|
| `KUSTO_CLUSTER` | ADX cluster URI, e.g. `https://<cluster>.<region>.kusto.windows.net` |
| `KUSTO_DB` | Database name (default `IoTDatabase`) |
| `KUSTO_TABLE` | Table the API queries (default `IoTSensorData`) |
| `AUTH_MODE` | `default` for managed identity / `az login` (recommended), or `app_key` for a service principal |
| `APP_ID` / `APP_SECRET` / `TENANT_ID` | Only required when `AUTH_MODE=app_key` |
| `ALLOWED_ORIGINS` | Comma-separated browser origins allowed to call the API |

With `AUTH_MODE=default` there is **no secret to create** — locally the API uses your `az login` session; in Azure it uses the App Service managed identity. Only set the `APP_*` values if you deliberately choose `AUTH_MODE=app_key`.

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
az login                            # DefaultAzureCredential uses this session
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
azure.yaml             azd service map (api → App Service, web → Static Web App)
infra/                 Bicep: ADX cluster + database, App Service, Static Web App
scripts/
  setup-adx.kql        Table schema + sample-data seed
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
.github/workflows/     CI: builds the frontend and import-smoke-tests the backend
```

## Security

- **Managed identity by default** — no client secret exists to leak or rotate. `AUTH_MODE=app_key` is an opt-in fallback only.
- Secrets (when `app_key` is used) are read from the environment only; no credentials belong in the repository.
- The API's identity holds least privilege — `Database Viewer` on the ADX database.
- CORS origins are allow-listed via `ALLOWED_ORIGINS`, never widened to `*` while credentials are allowed.

## License

MIT — see [LICENSE](LICENSE).
