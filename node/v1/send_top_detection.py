"""
send_top_detection.py
-----------------------

This script loads a BirdNET detection JSON file, selects the top (highest-confidence)
bird call, encodes it as a compact 8-byte Avis event, and transmits it over LoRa
using a RAK RUI3-based module.

Steps performed:
1. Load the detection JSON file (latest_detect.json by default)
2. Select the detection with the highest confidence value
3. Parse its timestamp and bin the confidence score into a 3-bit scale (0–7)
4. Use Protocol to encode a binary payload with timestamp, taxonomy, and confidence
5. Format and send the payload as a hexadecimal AT+SEND command over UART

Defaults:
- Detection file path: /home/FLC/enviropulse/latest_detect.json
- LoRa port: 1 (application-specific port used in AT command)

Assumes:
- JSON conforms to BirdNET-Pi output with keys: "detections", "common_name", "confidence", "timestamp"
- Taxonomy and confidence maps are preloaded via Protocol
- RUI3Driver handles low-level AT communication over UART (/dev/ttyS0)

This script is a manual dispatch tool to send a single detection event on demand.
It is modular and can be reused inside watchers, schedulers, or interactive scripts.

Run manually with:
  python3 send_top_detection.py
"""

#!/usr/bin/env python3
import json
from datetime import datetime
from pathlib import Path

from protocol import Protocol
from rui3_driver import RUI3Driver

# adjust these as needed
DETECT_JSON = Path('/home/FLC/enviropulse/latest_detect.json')
LORA_PORT    = 1  # application port number for AT+SEND

def get_conf_bin(raw_conf: float) -> int:
    """Map a 0.0–1.0 confidence to your 3-bit bin (0–7)."""
    bins = [
        (0.00, 0.50, 0),
        (0.51, 0.65, 1),
        (0.66, 0.74, 2),
        (0.75, 0.80, 3),
        (0.81, 0.85, 4),
        (0.86, 0.90, 5),
        (0.91, 0.95, 6),
        (0.96, 1.00, 7),
    ]
    for lo, hi, b in bins:
        if lo <= raw_conf <= hi:
            return b
    raise ValueError(f"Confidence {raw_conf} out of supported range")

def send_top_detection(json_path: Path, port: int = LORA_PORT):
    # 1) load the JSON and pick the highest‐confidence detection
    data = json.loads(json_path.read_text())
    dets = data.get("detections", [])
    if not dets:
        raise RuntimeError("No detections found in JSON")
    top = max(dets, key=lambda d: d.get("confidence", 0.0))

    # 2) extract fields
    common_name = top["common_name"]
    raw_conf    = float(top["confidence"])
    ts_str      = top.get("timestamp")
    if not ts_str:
        raise RuntimeError("No timestamp in top detection")
    # parse ISO8601 → UNIX seconds
    ts = int(datetime.fromisoformat(ts_str.replace("Z", "+00:00")).timestamp())

    # 3) bin the confidence
    conf_bin = get_conf_bin(raw_conf)

    # 4) build your Avis event payload
    proto     = Protocol()
    tax_code  = proto.encode_taxonomy(common_name)
    payload   = proto.encode_avis_event(ts, tax_code, conf_bin)

    # 5) form the AT command
    hex_payload = payload.hex().upper()  # e.g. "0A5F2D..."
    at_cmd      = f"AT+SEND={port}:{hex_payload}"

    # 6) send it over LoRa
    driver = RUI3Driver()
    print(f" Sending over LoRa: {at_cmd}")
    resp = driver.send_cmd(at_cmd)
    print(" Module response:", resp)
    driver.close()

if __name__ == "__main__":
    send_top_detection(DETECT_JSON, LORA_PORT)