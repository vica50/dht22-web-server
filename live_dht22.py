#!/home/victor/live-dht22-info/venv/bin/python
import Adafruit_DHT
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

sensor = Adafruit_DHT.DHT22
pin = 4  # GPIO4

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        if humidity is not None and temperature is not None:
            data = {
                "temperature": round(temperature, 1),
                "humidity": round(humidity, 1)
            }
        else:
            data = { "error": "Failed to read sensor" }
        self.wfile.write(json.dumps(data).encode())

server = HTTPServer(('', 8001), Handler)
print("Live DHT22 server running on port 8001...")
server.serve_forever()
