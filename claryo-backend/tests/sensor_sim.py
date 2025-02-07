# tests/sensor_sim.py

import time
import random
import json
from azure.iot.device import IoTHubDeviceClient, Message
import datetime


# Replace with actual connection string
CONNECTION_STRING = "HostName=claryo-mvp-iothub.azure-devices.net;DeviceId=claryo-sensor-sim;SharedAccessKey=BbgGShAbLsOVfZVbpTSKN/ceZYXJRopIecTJ5q3l48o="

# Configure for testing: send a fixed number of messages
NUM_MESSAGES = 10   # Number of test messages to send
DELAY_SECONDS = 5   # Delay between messages in seconds

def generate_telemetry():
    return {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "sensorId": "sensor-001",
        "pressure": round(random.uniform(5.0, 10.0), 2),
        "flowRate": round(random.uniform(0.0, 50.0), 2),
        "temperature": round(random.uniform(15.0, 30.0), 2)
    }

def main():
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
    print("Sending test messages to IoT Hub...")

    for i in range(NUM_MESSAGES):
        data_dict = generate_telemetry()
        data_json = json.dumps(data_dict)
        msg = Message(data_json)
        msg.content_encoding = "utf-8"
        msg.content_type = "application/json"

        client.send_message(msg)
        print(f"Sent message {i+1}: {data_json}")

        time.sleep(DELAY_SECONDS)

    print("Test message sending completed.")

if __name__ == "__main__":
    main()