import os
import io
import csv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from azure.kusto.data import KustoConnectionStringBuilder, KustoClient
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

app = FastAPI(title="Claryo API", version="0.1.0")

# Configure CORS so that requests from the React dev server (localhost:3000) are allowed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # or ["*"] to allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ADX connection settings loaded from environment variables
KUSTO_CLUSTER = os.getenv("KUSTO_CLUSTER")  # e.g., https://claryo-mvp-adx-cluster.northeurope.kusto.windows.net
KUSTO_DB = os.getenv("KUSTO_DB", "claryoMVPDB")
APP_ID = os.getenv("APP_ID")              # Your AAD App ID
APP_SECRET = os.getenv("APP_SECRET")      # Your AAD App Secret
TENANT_ID = os.getenv("TENANT_ID")        # Your Tenant ID

# Create the Kusto connection string builder and ADX client
kcsb = KustoConnectionStringBuilder.with_aad_application_key_authentication(
    KUSTO_CLUSTER,
    APP_ID,
    APP_SECRET,
    TENANT_ID
)
client = KustoClient(kcsb)

# Helper function to convert ADX query results (table rows) into a list of dictionaries.
def kusto_rows_to_dict(table):
    """
    Convert rows from an ADX table result into a list of dictionaries.
    Each dictionary is formed by pairing column names (from table.columns) with row values.
    """
    column_names = [col.column_name for col in table.columns]
    result = []
    for row in table:
        row_dict = {column_names[i]: row[i] for i in range(len(column_names))}
        result.append(row_dict)
    return result

# Root endpoint for basic health check
@app.get("/")
def read_root():
    return {"message": "Claryo FastAPI is running"}

# Endpoint to get the 10 most recent sensor data rows from IoTSensorData table
@app.get("/sensors/latest")
def get_latest_sensors():
    try:
        query = """
        IoTSensorData
        | order by timestamp desc
        | limit 10
        """
        response = client.execute(KUSTO_DB, query)
        rows = kusto_rows_to_dict(response.primary_results[0])
        return rows
    except Exception as e:
        print("Error in /sensors/latest:", e)
        return {"error": str(e)}

# Endpoint to get the average pressure over the last 10 records (for demonstration)
@app.get("/sensors/average_pressure_latest")
def get_average_pressure_latest():
    try:
        query = """
        IoTSensorData
        | order by timestamp desc
        | limit 10
        | summarize avgPressure = avg(pressure)
        """
        response = client.execute(KUSTO_DB, query)
        result = kusto_rows_to_dict(response.primary_results[0])
        return result
    except Exception as e:
        print("Error in /sensors/average_pressure_latest:", e)
        return {"error": str(e)}

# Example threshold for pressure alerts
THRESHOLD_PRESSURE = 8.0

# Endpoint to check alerts by comparing sensor pressure to a threshold
@app.get("/sensors/check_alerts")
def check_alerts(threshold: float = 12.0):
    try:
        query = """
        IoTSensorData
        | order by timestamp desc
        | limit 10
        """
        response = client.execute(KUSTO_DB, query)
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
        IoTSensorData
        | where timestamp > ago({hours}h)
        """
        response = client.execute(KUSTO_DB, query)
        rows = kusto_rows_to_dict(response.primary_results[0])

        if not rows:
            return {"message": "No data found for the specified period."}

        # Write the query results to an in-memory CSV file
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
