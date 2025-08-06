"""
dispatcher.py
-------------
Main controller for EnviroPulse runtime system.

- Reacts to new BirdNET detections using a DB file watcher
- Periodically samples weather and telemetry
- Routes all structured event dictionaries to the correct destination
  via their 'target' field, such as 'send_over_lora'

Supported event types:
- avis_event        (BirdNET)
- weather_event     (BMP390 + SHT31)
- telemetry_event   (Averaged GPS fix)
- birdnet_error     (fallback)

Targets:
- send_over_lora → transmit using Protocol + RUI3Driver
- log_only       → log to terminal
- noop           → ignore silently
"""

import time
import signal
import sys

from db_watcher import start_db_watch
from detection_extractor import get_latest_detection
from birdnet_sampler import BirdDetectionEvent
from weather_sampler import WeatherEvent
from telemetry_sampler import TelemetryEvent
from send_over_lora import send_event_over_lora

running = True

def handle_shutdown(sig, frame):
    global running
    print("Shutdown signal received.")
    running = False

def dispatch_event(event: dict):
    """Routes an event dictionary based on its 'target' field."""
    if not isinstance(event, dict):
        print("[ERROR] Non-dict event received. Skipping.")
        return

    target = event.get("target", "noop")
    event_type = event.get("event_type", "unknown")

    if event_type not in {"avis_event", "weather_event", "telemetry_event", "birdnet_error"}:
        print(f"[WARN] Unknown event_type: {event_type}")

    if target == "send_over_lora":
        send_event_over_lora(event)

    elif target == "log_only":
        print(f"[LOG] {event_type}: {event}")

    elif target == "noop":
        pass

    else:
        print(f"[WARN] Unknown target '{target}' for event: {event_type}")

def on_db_modified():
    """Triggered when BirdNET database changes."""
    row = get_latest_detection()
    if not row:
        return
    event = BirdDetectionEvent.from_row(row).to_dict()
    dispatch_event(event)

def sample_weather():
    try:
        event = WeatherEvent.from_sensors().to_dict()
        dispatch_event(event)
    except Exception as e:
        print(f"[ERROR] Weather sample failed: {e}")

def sample_telemetry():
    try:
        event = TelemetryEvent.from_gps().to_dict()
        dispatch_event(event)
    except Exception as e:
        print(f"[ERROR] Telemetry sample failed: {e}")

def main_loop():
    print("Dispatcher starting...")
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    observer = start_db_watch(on_db_modified)

    try:
        weather_interval = 5 * 60
        telemetry_interval = 5 * 60

        next_weather = time.time()
        next_telemetry = time.time()

        while running:
            now = time.time()

            if now >= next_weather:
                sample_weather()
                next_weather = now + weather_interval

            if now >= next_telemetry:
                sample_telemetry()
                next_telemetry = now + telemetry_interval

            time.sleep(1)

    finally:
        observer.stop()
        observer.join()
        print("Dispatcher stopped.")

if __name__ == "__main__":
    if len(sys.argv) == 2:
        arg = sys.argv[1]
        if arg == "--weather":
            sample_weather()
            sys.exit(0)
        elif arg == "--telemetry":
            sample_telemetry()
            sys.exit(0)

    main_loop()