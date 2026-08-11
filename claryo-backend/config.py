# claryo-backend/config.py

import os
from dotenv import load_dotenv

# Load variables from a local .env file when present (ignored in Azure).
load_dotenv()


class Config:
    # --- Azure Data Explorer (Kusto) ---
    KUSTO_CLUSTER = os.getenv("KUSTO_CLUSTER")  # https://<cluster>.<region>.kusto.windows.net
    KUSTO_DB = os.getenv("KUSTO_DB", "IoTDatabase")
    KUSTO_TABLE = os.getenv("KUSTO_TABLE", "IoTSensorData")

    # --- Authentication ---
    # "default": DefaultAzureCredential — managed identity in Azure, `az login` locally. No secret needed.
    # "app_key": Microsoft Entra service principal with a client secret (fill APP_ID/APP_SECRET/TENANT_ID).
    AUTH_MODE = os.getenv("AUTH_MODE", "default").lower()
    APP_ID = os.getenv("APP_ID")
    APP_SECRET = os.getenv("APP_SECRET")
    TENANT_ID = os.getenv("TENANT_ID")

    # --- CORS ---
    # Comma-separated list of browser origins allowed to call the API.
    ALLOWED_ORIGINS = [
        o.strip()
        for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
        if o.strip()
    ]