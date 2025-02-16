from influxdb_client import InfluxDBClient, Point
import os
from dotenv import load_dotenv

load_dotenv()

token = os.environ["INFLUX_TOKEN"]

# Initialize InfluxDB client
client = InfluxDBClient(url="http://localhost:8086", token=token, org="docs")
write_api = client.write_api()


def log_attendance(event_log):
    point = (
        Point("attendance_log")  # Measurement name
        .tag("type", event_log["type"])  # Type (login/logout)
        .tag("worksite_id", event_log["data"]["worksite_id"])  # Worksite
        .tag("employee_id", event_log["data"]["employee_id"])  # Employee ID
        .field("timestamp", event_log["data"]["time"])  # Store time as a field
    )

    write_api.write(bucket="logs", record=point)
    print(f"Logged: {event_log}")
