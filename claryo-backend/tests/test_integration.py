# claryo-backend/tests/test_integration.py

import time
import pytest
from fastapi.testclient import TestClient
from main import app
from tests.sensor_sim import generate_telemetry

# --- Fake ADX Response Classes --- #
class FakeADXColumn:
    def __init__(self, name):
        self.column_name = name

class FakeADXTable:
    def __init__(self, rows):
        self._rows = rows
        # Assume all rows have the same keys.
        if rows:
            self.columns = [FakeADXColumn(name) for name in rows[0].keys()]
        else:
            self.columns = []
    def __iter__(self):
        # For each row, yield the values in the order of the columns.
        for row in self._rows:
            yield [row[col.column_name] for col in self.columns]

class FakeADXResponse:
    def __init__(self, rows):
        self.primary_results = [FakeADXTable(rows)]

# --- Integration Test --- #
client = TestClient(app)

def test_end_to_end_flow(mocker):
    """
    Simulate the sensor data generation and test that the /sensors/latest endpoint
    returns the simulated data. This integration test uses mocking to replace the
    ADX query execution with a fake response.
    """
    # Generate simulated telemetry data.
    simulated_data = generate_telemetry()
    
    # Create a fake ADX response that returns our simulated telemetry record.
    fake_rows = [simulated_data]
    fake_response = FakeADXResponse(fake_rows)
    
    # Use pytest-mock's mocker fixture to patch main.client.execute.
    # Here, we assume that the /sensors/latest endpoint calls client.execute exactly once.
    mocker.patch("main.client.execute", return_value=fake_response)
    
    # Optionally, wait a short time to simulate processing delay (if needed).
    time.sleep(1)
    
    # Call the /sensors/latest endpoint.
    response = client.get("/sensors/latest")
    assert response.status_code == 200, "Expected 200 OK from /sensors/latest"
    
    data = response.json()
    # Check that the response is a list and contains our simulated sensorId.
    assert isinstance(data, list), "Expected response to be a list"
    sensor_ids = [d.get("sensorId") for d in data]
    assert simulated_data["sensorId"] in sensor_ids, "Simulated sensorId not found in API response"
    
    # You can add further tests for summary endpoints similarly.
    # For example, test the temperature summary endpoint:
    mocker.patch("main.client.execute", return_value=FakeADXResponse(fake_rows))
    temp_response = client.get("/sensors/temperature_summary?dateRange=Last%207%20Days")
    assert temp_response.status_code == 200, "Expected 200 OK from /sensors/temperature_summary"
    temp_data = temp_response.json()
    assert "chartData" in temp_data and "metrics" in temp_data, "Expected chartData and metrics in temperature summary"