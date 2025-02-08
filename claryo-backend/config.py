# claryo-backend/config.py

import os
from dotenv import load_dotenv

# Load variables from the .env file (this file should be in claryo-backend)
load_dotenv()

class Config:
    KUSTO_CLUSTER = os.getenv("KUSTO_CLUSTER")  # e.g., "https://your-cluster-url"
    KUSTO_DB = os.getenv("KUSTO_DB", "claryoMVPDB")
    APP_ID = os.getenv("APP_ID")
    APP_SECRET = os.getenv("APP_SECRET")
    TENANT_ID = os.getenv("TENANT_ID")