# claryo-backend/tests/test_telemetry.py

import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from main import app  # Ensure main.py exports your FastAPI app
from tests.sensor_sim import generate_telemetry  # Import your sensor simulation function

# Create a TestClient for the FastAPI app.
client = TestClient(app)


# -------------------------------
# Unit Tests for Telemetry Generation
# -------------------------------

def test_generate_telemetry_structure():
    """Test that the generated telemetry contains the required keys."""
    data = generate_telemetry()
    expected_keys = {"timestamp", "sensorId", "pressure", "flowRate", "temperature"}
    assert expected_keys.issubset(data.keys()), f"Missing keys in telemetry data: {data.keys()}"

def test_generate_telemetry_ranges():
    """Test that the sensor values fall within expected ranges."""
    data = generate_telemetry()
    # Example expected ranges:
    assert 15 <= data["temperature"] <= 30, f"Temperature {data['temperature']} out of range"
    assert 5.0 <= data["pressure"] <= 10.0, f"Pressure {data['pressure']} out of range"
    assert 0 <= data["flowRate"] <= 50, f"FlowRate {data['flowRate']} out of range"


# -------------------------------
# Integration Tests for API Endpoints
# -------------------------------

def test_get_latest_sensors():
    """Test the /sensors/latest endpoint."""
    response = client.get("/sensors/latest")
    assert response.status_code == 200, "Expected status code 200 from /sensors/latest"
    data = response.json()
    assert isinstance(data, list), "Expected a list from /sensors/latest"
    if data:
        expected_keys = {"timestamp", "sensorId", "pressure", "flowRate", "temperature"}
        assert expected_keys.issubset(data[0].keys()), "Missing expected keys in latest sensor data"

def test_temperature_summary_endpoint():
    """Test the /sensors/temperature_summary endpoint."""
    response = client.get("/sensors/temperature_summary?dateRange=Last%207%20Days")
    assert response.status_code == 200, "Expected status code 200 from /sensors/temperature_summary"
    data = response.json()
    assert "chartData" in data and "metrics" in data, "Expected chartData and metrics keys in response"
    assert isinstance(data["chartData"], list), "Expected chartData to be a list"
    assert isinstance(data["metrics"], list), "Expected metrics to be a list"
    # Optionally, check that at least one data point exists:
    # assert len(data["chartData"]) > 0

def test_pressure_summary_endpoint():
    """Test the /sensors/pressure_summary endpoint."""
    response = client.get("/sensors/pressure_summary?dateRange=Last%207%20Days")
    assert response.status_code == 200, "Expected status code 200 from /sensors/pressure_summary"
    data = response.json()
    assert "chartData" in data and "metrics" in data, "Expected chartData and metrics keys in pressure summary response"
    assert isinstance(data["chartData"], list), "Expected chartData to be a list"
    assert isinstance(data["metrics"], list), "Expected metrics to be a list"

def test_flow_summary_endpoint():
    """Test the /sensors/flow_summary endpoint."""
    response = client.get("/sensors/flow_summary?dateRange=Last%207%20Days")
    assert response.status_code == 200, "Expected status code 200 from /sensors/flow_summary"
    data = response.json()
    assert "chartData" in data and "metrics" in data, "Expected chartData and metrics keys in flow summary response"
    assert isinstance(data["chartData"], list), "Expected chartData to be a list"
    assert isinstance(data["metrics"], list), "Expected metrics to be a list"

# -------------------------------
# (Optional) Integration Test for End-to-End Data Flow
# -------------------------------
def test_end_to_end_flow():
    """
    Test the entire data flow:
    - Simulate telemetry generation.
    - Wait a moment for data ingestion (if needed).
    - Query the /sensors/latest endpoint to confirm the simulated data is present.
    """
    # Generate simulated telemetry data
    simulated = generate_telemetry()
    # (In a full integration test, you might actually send this data to the IoT Hub,
    # then verify ingestion into ADX. Here we simply check the API.)
    
    # Wait a few seconds to allow data ingestion (if applicable)
    import time
    time.sleep(5)
    
    response = client.get("/sensors/latest")
    assert response.status_code == 200, "Expected status code 200 from /sensors/latest after simulation"
    sensor_data = response.json()
    # Check that at least one record matches the simulated sensorId.
    matching = [d for d in sensor_data if d.get("sensorId") == simulated.get("sensorId")]
    assert matching, "No sensor data matching the simulated sensorId was found in /sensors/latest"