import os
import io
import csv
import datetime
from typing import Optional, Tuple, List, Dict
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from azure.kusto.data import KustoConnectionStringBuilder, KustoClient
from azure.identity import DefaultAzureCredential
from config import Config




app = FastAPI(title="Claryo API", version="0.1.0")

# CORS origins are configurable so the app works in any deployment (see ALLOWED_ORIGINS).
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ADX connection settings loaded from environment variables
KUSTO_CLUSTER = Config.KUSTO_CLUSTER
KUSTO_DB = Config.KUSTO_DB
TABLE = Config.KUSTO_TABLE

# The ADX client is created lazily so the app can be imported without credentials
# (e.g. in CI or unit tests) and so a misconfigured cluster fails on request, not import.
_client = None


def get_client() -> KustoClient:
    global _client
    if _client is not None:
        return _client
    if not KUSTO_CLUSTER:
        raise RuntimeError("KUSTO_CLUSTER is not set — see .env.example.")
    if Config.AUTH_MODE == "app_key":
        if not all([Config.APP_ID, Config.APP_SECRET, Config.TENANT_ID]):
            raise RuntimeError(
                "AUTH_MODE=app_key requires APP_ID, APP_SECRET and TENANT_ID."
            )
        kcsb = KustoConnectionStringBuilder.with_aad_application_key_authentication(
            KUSTO_CLUSTER, Config.APP_ID, Config.APP_SECRET, Config.TENANT_ID
        )
    else:
        # DefaultAzureCredential: managed identity in Azure, `az login` locally.
        kcsb = KustoConnectionStringBuilder.with_azure_token_credential(
            KUSTO_CLUSTER, DefaultAzureCredential()
        )
    _client = KustoClient(kcsb)
    return _client

# Helper function to convert ADX query results (table rows) into a list of dictionaries.
def kusto_rows_to_dict(table) -> List[Dict]:
    column_names = [col.column_name for col in table.columns]
    result = []
    for row in table:
        row_dict = {column_names[i]: row[i] for i in range(len(column_names))}
        result.append(row_dict)
    return result

# Helper: Determine the start and end dates based on the dateRange parameter.
def get_date_range(dateRange: str) -> Tuple[datetime.datetime, datetime.datetime]:
    if dateRange == "Last 7 Days":
        end_date = datetime.datetime.now(datetime.timezone.utc)
        start_date = end_date - datetime.timedelta(days=7)
    elif dateRange == "Last Month":
        end_date = datetime.datetime.now(datetime.timezone.utc)
        start_date = end_date - datetime.timedelta(days=30)
    else:
        end_date = datetime.datetime.now(datetime.timezone.utc)
        start_date = end_date - datetime.timedelta(days=30)
    return start_date, end_date

# Helper: Execute a query and return chart data.
def get_chart_data(field: str, alias: str, start_date: datetime.datetime, end_date: datetime.datetime) -> List[Dict]:
    query = f"""
        {TABLE}
        | where timestamp between (datetime({start_date.isoformat()}) .. datetime({end_date.isoformat()}))
        | summarize {alias} = avg({field}) by bin(timestamp, 1h)
        | order by timestamp asc
    """
    print(f"{field.capitalize()} Summary Query:", query)
    response = get_client().execute(KUSTO_DB, query)
    chart_data = []
    primary_results = response.primary_results[0]
    columns = [col.column_name for col in primary_results.columns]
    for row in primary_results:
        data_point = {columns[i]: row[i] for i in range(len(columns))}
        chart_data.append(data_point)
    return chart_data

# Helper: Execute a query to compute summary metrics.
def get_metrics(field: str, min_alias: str, max_alias: str, start_date: datetime.datetime, end_date: datetime.datetime) -> List[Dict]:
    query = f"""
        {TABLE}
        | where timestamp between (datetime({start_date.isoformat()}) .. datetime({end_date.isoformat()}))
        | summarize current = arg_max(timestamp, {field}), {min_alias} = min({field}), {max_alias} = max({field})
    """
    print(f"{field.capitalize()} Metric Query:", query)
    response = get_client().execute(KUSTO_DB, query)
    raw_metrics = kusto_rows_to_dict(response.primary_results[0])
    if raw_metrics:
        metric = raw_metrics[0]
        # Construct a metric object with a label and standardized keys.
        if field == "temperature":
            return [{
                "label": "Temperature",
                "current": metric.get("temperature", "-"),
                "min": metric.get("minTemp", "-"),
                "max": metric.get("maxTemp", "-")
            }]
        elif field == "pressure":
            return [{
                "label": "Pressure",
                "current": metric.get("pressure", "-"),
                "min": metric.get("minPressure", "-"),
                "max": metric.get("maxPressure", "-")
            }]
        elif field == "flowRate":
            return [{
                "label": "Flow",
                "current": metric.get("flowRate", "-"),
                "min": metric.get("minFlow", "-"),
                "max": metric.get("maxFlow", "-")
            }]
    return []

# Helper: Combine the above functions into a single summary retrieval function.
def get_summary(field: str, chart_alias: str, min_alias: str, max_alias: str, dateRange: str) -> Dict:
    start_date, end_date = get_date_range(dateRange)
    chart_data = get_chart_data(field, chart_alias, start_date, end_date)
    metrics = get_metrics(field, min_alias, max_alias, start_date, end_date)
    return {"chartData": chart_data, "metrics": metrics}

# Root endpoint for basic health check
@app.get("/")
def read_root():
    return {"message": "Claryo FastAPI is running"}

# Endpoint to get the 10 most recent sensor data rows from IoTSensorData table
@app.get("/sensors/latest")
def get_latest_sensors():
    try:
        query = f"""
        {TABLE}
        | order by timestamp desc
        | limit 10
        """
        response = get_client().execute(KUSTO_DB, query)
        rows = kusto_rows_to_dict(response.primary_results[0])
        return rows
    except Exception as e:
        print("Error in /sensors/latest:", e)
        return {"error": str(e)}

# Endpoint to get the average pressure over the last 10 records (for demonstration)
@app.get("/sensors/average_pressure_latest")
def get_average_pressure_latest():
    try:
        query = f"""
        {TABLE}
        | order by timestamp desc
        | limit 10
        | summarize avgPressure = avg(pressure)
        """
        response = get_client().execute(KUSTO_DB, query)
        result = kusto_rows_to_dict(response.primary_results[0])
        return result
    except Exception as e:
        print("Error in /sensors/average_pressure_latest:", e)
        return {"error": str(e)}

# Endpoint to check alerts by comparing sensor pressure to a threshold
THRESHOLD_PRESSURE = 8.0
@app.get("/sensors/check_alerts")
def check_alerts(threshold: float = 12.0):
    try:
        query = f"""
        {TABLE}
        | order by timestamp desc
        | limit 10
        """
        response = get_client().execute(KUSTO_DB, query)
        rows = kusto_rows_to_dict(response.primary_results[0])
        alerts_triggered = []
        for row in rows:
            if row.get("pressure", 0) > threshold:
                alerts_triggered.append({
                    "sensorId": row.get("sensorId"),
                    "pressure": row.get("pressure"),
                    "timestamp": row.get("timestamp")
                })
        return {
            "rows_checked": len(rows),
            "alerts_triggered": alerts_triggered
        }
    except Exception as e:
        print("Error in /sensors/check_alerts:", e)
        return {"error": str(e)}

# Endpoint to export sensor data as CSV; query data from the past N hours
@app.get("/export")
def export_data(hours: int = 1):
    try:
        query = f"""
        {TABLE}
        | where timestamp > ago({hours}h)
        """
        response = get_client().execute(KUSTO_DB, query)
        rows = kusto_rows_to_dict(response.primary_results[0])
        if not rows:
            return {"message": "No data found for the specified period."}
        csv_buffer = io.StringIO()
        writer = csv.DictWriter(csv_buffer, fieldnames=rows[0].keys())
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
        csv_buffer.seek(0)
        return StreamingResponse(
            csv_buffer,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=claryo_export.csv"}
        )
    except Exception as e:
        print("Error in /export:", e)
        return {"error": str(e)}

# -----------------------------
# Optimized Summary Endpoints
# -----------------------------

@app.get("/sensors/temperature_summary")
def temperature_summary(dateRange: str = Query(...)):
    # For temperature, use field "temperature", chart alias "avgTemp", metric aliases "minTemp" and "maxTemp"
    return get_summary("temperature", "avgTemp", "minTemp", "maxTemp", dateRange)

@app.get("/sensors/pressure_summary")
def pressure_summary(dateRange: str = Query(...)):
    # For pressure, use field "pressure", chart alias "avgPressure", metric aliases "minPressure" and "maxPressure"
    return get_summary("pressure", "avgPressure", "minPressure", "maxPressure", dateRange)

@app.get("/sensors/flow_summary")
def flow_summary(dateRange: str = Query(...)):
    # For flow, use field "flowRate", chart alias "avgFlow", metric aliases "minFlow" and "maxFlow"
    return get_summary("flowRate", "avgFlow", "minFlow", "maxFlow", dateRange)