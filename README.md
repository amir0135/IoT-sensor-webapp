# IoT Dashboard

Claryo Dashboard is a real-time monitoring application for sensor data (e.g., pressure, flow rate, and temperature) sourced from an Azure Data Explorer (ADX) database. The platform consists of a FastAPI backend that queries sensor data from ADX and a React frontend that displays various dashboards, alerts, and summaries with dynamic charts and metrics.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Setup and Installation](#setup-and-installation)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Environment Configuration](#environment-configuration)
- [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Frontend Pages](#frontend-pages)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features

- **Real-Time Data:** Polls and displays recent sensor data from ADX.
- **Dynamic Dashboards:** Separate pages for Temperature, Pressure, and Flow dashboards.
- **Combined Summary:** Overview chart aggregating key sensor information.
- **Alerts Panel:** Real-time monitoring of sensor values based on customizable thresholds.
- **Responsive UI:** Built with React, React Router, and styled-components.
- **Robust Backend:** FastAPI endpoints that query and summarize sensor data using ADX Kusto.

## Architecture

- **Backend:**  
  Built with [FastAPI](https://fastapi.tiangolo.com), the backend queries sensor data from an Azure Data Explorer (ADX) cluster using the `azure.kusto.data` package. Key endpoints include:
  - `/sensors/latest`
  - `/sensors/average_pressure_latest`
  - `/sensors/temperature_summary`
  - `/sensors/pressure_summary`
  - `/sensors/flow_summary`
  - `/sensors/check_alerts`
  - `/export`
- **Frontend:**  
  Developed with [React](https://reactjs.org) and using [react-router-dom](https://reactrouter.com/en/main) for routing, the frontend features multiple dashboards (Temperature, Pressure, Flow, and a Combined Summary) and an Alerts Panel for real-time sensor alerts.

## Prerequisites

- **Backend:**
  - Python 3.8+
  - FastAPI
  - Uvicorn
  - Azure Kusto SDK (`azure-kusto-data`)
  - pip (or a similar tool)
- **Frontend:**
  - Node.js 14+
  - npm or yarn

## Setup and Installation

### Backend Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/claryo-dashboard.git
   cd claryo-dashboard/claryo-backend
   ```

2. **Create and activate a virtual environment (optional but recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the required packages:**

   ```bash
   pip install -r requirements.txt
   ```

   *Note: Ensure that your `requirements.txt` file includes dependencies such as `fastapi`, `uvicorn`, `azure-kusto-data`, and others.*

4. **Configure Environment Variables:**

   Create a `.env` file in the `claryo-backend` directory with the following variables:

   ```ini
   KUSTO_CLUSTER=https://your-adx-cluster.region.kusto.windows.net
   KUSTO_DB=yourDatabaseName
   APP_ID=yourAADApplicationID
   APP_SECRET=yourAADApplicationSecret
   TENANT_ID=yourTenantID
   ```

5. **Run the Backend Server:**

   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup

1. **Navigate to the frontend directory:**

   ```bash
   cd ../claryo-frontend
   ```

2. **Install dependencies:**

   *Using npm (with legacy peer-deps flag if necessary):*

   ```bash
   npm install --legacy-peer-deps
   ```
   *Alternatively, you may use:*
   ```bash
   npm install --force
   ```

3. **Run the Frontend Server:**

   ```bash
   npm start
   ```

## Environment Configuration

- Ensure that your backend `.env` file is correctly configured with ADX connection information.
- In the frontend, verify the `package.json` dependencies for `react-router-dom`, `styled-components`, and other libraries.

## Running the Application

- **Backend:** Running on (e.g.) `http://localhost:8000`
- **Frontend:** Running on (e.g.) `http://localhost:3000`
- Use the provided navigation buttons and URL routes (e.g., `/dashboard/temperature`, `/dashboard/pressure`, `/dashboard/flow`, `/dashboard/combined`) to navigate through dashboards.

## Project Structure 
