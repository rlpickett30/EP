# gps_averager.py

import time
import statistics
from datetime import datetime
from rui3_driver import RUI3Driver
from node_gps_driver import get_gps_data  # must return a dict with keys 'lat' and 'lon'

AVERAGE_INTERVAL_SEC = 15 * 60  # 15 minutes
SAMPLE_INTERVAL_SEC = 10        # every 10 seconds

def main():
    lat_samples = []
    lon_samples = []

    driver = RUI3Driver(port="/dev/ttyUSB0")  # Adjust if needed

    start_time = time.time()
    while True:
        gps = get_gps_data()
        if gps and gps.get("lat") and gps.get("lon"):
            lat_samples.append(gps["lat"])
            lon_samples.append(gps["lon"])

        time.sleep(SAMPLE_INTERVAL_SEC)

        # If 15 minutes have passed, send average and reset
        if time.time() - start_time >= AVERAGE_INTERVAL_SEC:
            if lat_samples and lon_samples:
                avg_lat = statistics.mean(lat_samples)
                avg_lon = statistics.mean(lon_samples)

                # Format: "avg_loc:<lat>,<lon>"
                msg = f"avg_loc:{avg_lat:.6f},{avg_lon:.6f}"
                print(f"[{datetime.now()}] Sending: {msg}")
                response = driver.send(msg)
                print(f"Module replied: {response}")

            lat_samples.clear()
            lon_samples.clear()
            start_time = time.time()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}")
