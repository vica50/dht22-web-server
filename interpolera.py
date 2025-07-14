#!/home/victor/live-dht22-info/venv/bin/python
from datetime import datetime, timedelta

start = {"hum": 39.1, "temp": 24.8, "time": "2025-07-13 23:07:41"}
end = {"hum": 37.8, "temp": 29.6, "time": "2025-07-14 09:41:32"}

start_time = datetime.strptime(start["time"], "%Y-%m-%d %H:%M:%S")
end_time = datetime.strptime(end["time"], "%Y-%m-%d %H:%M:%S")

interval = timedelta(minutes=5)
total_seconds = (end_time - start_time).total_seconds()
steps = int(total_seconds // interval.total_seconds())

for i in range(steps + 1):
    t = i / steps
    current_time = start_time + i * interval
    time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")

    temp = start["temp"] + t * (end["temp"] - start["temp"])
    hum = start["hum"] + t * (end["hum"] - start["hum"])

    # Format enligt exemplet med exakta mellanslag
    print(f'{{"time": "{time_str}", "temp": {round(temp, 1)}, "hum": {round(hum, 1)}}}')
