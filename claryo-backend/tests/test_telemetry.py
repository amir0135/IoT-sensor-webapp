# claryo-backend/tests/test_telemetry.py

from claryo_backend.tests.sensor_sim import generate_telemetry

def test_generate_telemetry_structure():
    data = generate_telemetry()
    expected_keys = {"timestamp", "sensorId", "pressure", "flowRate", "temperature"}
    assert expected_keys.issubset(data.keys())