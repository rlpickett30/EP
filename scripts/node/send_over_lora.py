"""
send_over_lora.py
-----------------

Handles LoRa transmission of any structured EnviroPulse event.

This module accepts a dictionary representing one of:
  - Bird detection ("avis_event")
  - Weather telemetry ("weather_event")
  - System metrics ("telemetry_event")
  - Error logs or alerts

The event dictionary must contain:
    - event_type:     str   (e.g., "avis_event", "weather_event")
    - target:         str   (used by dispatcher, not touched here)
    - other fields:   required by Protocol for that event type

Responsibilities:
- Encodes the event using Protocol
- Transmits it over UART using RUI3Driver and AT+SEND

This script does not determine event type—it encodes what it’s given.
"""

from protocol import Protocol
from rui3_driver import RUI3Driver

def send_event_over_lora(event: dict, port: int = 1):
    """Encodes and sends an EnviroPulse event over LoRa via RUI3 AT+SEND."""
    proto = Protocol()
    
    try:
        payload = proto.encode(event)
    except Exception as e:
        print(f"[ERROR] Protocol encoding failed: {e}")
        return

    hex_payload = payload.hex().upper()
    at_cmd = f"AT+SEND={port}:{hex_payload}"

    try:
        driver = RUI3Driver()
        print(f"Sending over LoRa: {at_cmd}")
        resp = driver.send_cmd(at_cmd)
        print("Module response:", resp)
        driver.close()
    except Exception as e:
        print(f"[ERROR] LoRa transmission failed: {e}")
