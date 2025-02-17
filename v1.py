import argparse
import cv2
import torch
import numpy as np
import subprocess
import time
from ultralytics import YOLO
from influxdb import InfluxDBClient
from dotenv import load_dotenv
import os

load_dotenv()

def update_config(cid):
    config_path = "/root/jaefar/mtx/mediamtx.yml"
    new_entry = f"    convert_{cid}_v1:\n        source: rtsp://localhost:8554/v1/{cid}\n        sourceOnDemand: yes\n"
    
    with open(config_path, "r") as file:
        lines = file.readlines()
    
    updated_lines = []
    paths_found = False
    inserted = False
    
    for line in lines:
        updated_lines.append(line)
        if line.strip() == "paths:":
            paths_found = True
        elif paths_found and not inserted and line.strip() == "all_others:":
            updated_lines.insert(-1, new_entry)
            inserted = True
    
    if not paths_found:
        raise ValueError("Could not find 'paths:' in the configuration file.")
    if not inserted:
        raise ValueError("Could not insert before 'all_others:' in the configuration file.")
    
    with open(config_path, "w") as file:
        file.writelines(updated_lines)

def log_to_influx(client, cid, class_counts):
    """Logs object counts to InfluxDB with a timestamp."""
    json_body = [
        {
            "measurement": "object_counts",
            "tags": {
                "client_id": cid
            },
            "time": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            "fields": class_counts
        }
    ]
    client.write_points(json_body)

def process_stream(cid, r_url):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    model = YOLO("yolov8n.pt").to(device)
    
    width, height = 1280, 720
    output_rtsp_url = f"rtsp://localhost:8554/v1/{cid}"
    ffmpeg_command = [
        "ffmpeg", "-y", "-re",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-pix_fmt", "bgr24", "-s", f"{width}x{height}", "-r", "30",
        "-i", "-",
        "-c:v", "libx264", "-preset", "veryfast", "-tune", "zerolatency",
        "-rtsp_transport", "tcp",
        "-f", "rtsp", output_rtsp_url
    ]

    # Initialize InfluxDB client
    token = os.getenv("INFLUX_TOKEN")
    influx_client = InfluxDBClient(host="localhost", port=8086, token=token, database="object_tracking")
    
    prev_counts = {}  # Previous object count

    while True:
        try:
            cap = cv2.VideoCapture(r_url)
            if not cap.isOpened():
                raise Exception("Error: Cannot open RTSP stream")
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            ffmpeg = subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE)
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    raise Exception("Error: Cannot read frame")
                
                frame = cv2.resize(frame, (width, height))
                results = model(frame)

                class_counts = {}  # Current object count

                if results:
                    result = results[0]
                    for box in result.boxes:
                        cls = int(box.cls[0])
                        class_name = model.names[cls]
                        class_counts[class_name] = class_counts.get(class_name, 0) + 1

                        # Draw bounding boxes
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        conf = box.conf[0]
                        label = f"{class_name} {conf:.2f}"
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(frame, label, (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # Check if class counts changed
                if class_counts != prev_counts:
                    log_to_influx(influx_client, cid, class_counts)
                    prev_counts = class_counts.copy()

                ffmpeg.stdin.write(frame.tobytes())

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)  # Wait before retrying
        finally:
            cap.release()
            ffmpeg.stdin.close()
            ffmpeg.wait()
            influx_client.close()

def main():
    parser = argparse.ArgumentParser(description="Update mediamtx.yml and process RTSP stream for v1.")
    parser.add_argument("--cid", required=True, help="Client ID")
    parser.add_argument("--r_url", required=True, help="RTSP input URL")
    args = parser.parse_args()
    
    update_config(args.cid)
    process_stream(args.cid, args.r_url)

if __name__ == "__main__":
    main()

