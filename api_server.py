#!/home/victor/live-dht22-info/venv/bin/python
from flask import Flask, jsonify, send_from_directory, request
import os
import adafruit_dht
import board
import threading
import time
import json
from datetime import datetime, timedelta

app = Flask(__name__, static_folder='static', static_url_path='/dht22/static')

# Sensor setup
dhtDevice = adafruit_dht.DHT22(board.D4)

# Data logging setup
DATA_FILE = "data.jsonl"
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Serve the index.html
@app.route("/dht22/")
def serve_index():
    return send_from_directory("static", "index.html")

# API: live reading
@app.route("/dht22/api/live")
def get_live():
    try:
        time.sleep(2)
        temp = dhtDevice.temperature
        humidity = dhtDevice.humidity
        return jsonify({
            "temperature": temp,
            "humidity": humidity
        })
    except Exception as e:
        return jsonify({"error": str(e)})

# API: live CPU temp
@app.route("/dht22/api/cpu_temp")
def get_cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp_str = f.read().strip()
            temp_c = int(temp_str) / 1000.0
        return jsonify({"cpu_temp": round(temp_c, 1)})
    except Exception as e:
        return jsonify({"error": str(e)})

# API: fetch logged data
@app.route("/dht22/api/data")
def get_data():
    data = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            for line in f:
                try:
                    data.append(json.loads(line))
                except:
                    continue

    range_val = request.args.get("range", "all")
    if range_val != "all":
        now = datetime.now()
        cutoff = None

        if range_val == "1d":
            cutoff = now - timedelta(days=1)
        elif range_val == "1w":
            cutoff = now - timedelta(weeks=1)
        elif range_val == "1y":
            cutoff = now - timedelta(days=365)
        elif range_val == "ch":
            try:
                hours = int(request.args.get("h", "1"))
                cutoff = now - timedelta(hours=hours)
            except:
                cutoff = None
        elif range_val == "cd":
            try:
                days = int(request.args.get("d", "1"))
                cutoff = now - timedelta(days=days)
            except:
                cutoff = None

        if cutoff:
            filtered = []
            for entry in data:
                try:
                    entry_time = datetime.strptime(entry["time"], "%Y-%m-%d %H:%M:%S")
                    if entry_time >= cutoff:
                        filtered.append(entry)
                except:
                    continue
            data = filtered

    return jsonify(data)

# Background: log sensor data every 5 minutes
def log_sensor_data():
    while True:
        try:
            temp = dhtDevice.temperature
            hum = dhtDevice.humidity
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            entry = {"time": timestamp, "temp": temp, "hum": hum}

            with open(DATA_FILE, "a") as f:
                f.write(json.dumps(entry) + "\n")

            trim_data_file()
        except Exception as e:
            print("Logging error:", e)
        time.sleep(300)  # wait 5 min

# Trim old data if file too large
def trim_data_file():
    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > MAX_FILE_SIZE:
        with open(DATA_FILE, "r") as f:
            lines = f.readlines()

        # Keep last 70%
        keep_lines = lines[-int(len(lines)*0.7):]
        with open(DATA_FILE, "w") as f:
            f.writelines(keep_lines)

# Start background thread
def start_logger():
    thread = threading.Thread(target=log_sensor_data)
    thread.daemon = True
    thread.start()

start_logger()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)

