"""
dispatcher.py
-------------

Main UDP event dispatcher for the EnviroPulse gateway.

Responsibilities:
- Initialize and manage the UDP listener for LoRaWAN traffic
- Load per-node AppSKeys from the node registry
- Decode incoming rxpk packets using the Protocol class
- Log decoded results to date-based daily JSON log files
- Dispatch events to appropriate internal subsystems (web_ingestor, weather, telemetry)

Stability:
- Uses structured try/except blocks for pipeline fault tolerance
- Decoding and routing failures are logged but do not crash the loop
- Duplicate packets are ignored using in-memory signature cache

Dependencies:
- udp_listener.py      ← UDP interface for LoRaWAN Semtech protocol
- udp_decoder.py       ← LoRaEvent class for parsing + decoding packets
- udp_logger.py        ← Daily rotating log system
- web_ingestor.py      ← Posts bird detections to your web API
- node_registry.json   ← AppSKey mapping for node DevAddr

Location:
  Place this file in: EP/scripts/server/
"""

import json
from pathlib import Path
from collections import deque

from udp_listener import UDPListener
from udp_decoder import LoRaEvent
from udp_logger import Logger
from web_ingestor import ingest_avis_event


# ─── Configurable Paths ─────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
REGISTRY_PATH = BASE_DIR / "node_registry.json"
LOG_PATH = BASE_DIR.parent.parent / "logs"

# ─── Load AppSKey Registry ─────────────────────────────────────────
try:
    with open(REGISTRY_PATH) as f:
        NODE_REGISTRY = json.load(f)
except Exception as e:
    print(f"[dispatcher] Failed to load node registry: {e}")
    NODE_REGISTRY = {}

# ─── Init Logger and Dedupe Memory ─────────────────────────────────
logger = Logger(base_dir=LOG_PATH)
SEEN = deque(maxlen=100)


# ─── Subsystem Routing Hooks ───────────────────────────────────────
def handle_web_ingestor(event: dict):
    ingest_avis_event(event)


def handle_weather(event: dict):
    print("[dispatcher] [weather] Event:", event)


def handle_telemetry(event: dict):
    print("[dispatcher] [telemetry] Event:", event)


# ─── LoRaWAN Packet Handler ────────────────────────────────────────
def handle_push_data(payload, addr):
    for rxpk in payload.get("rxpk", []):
        try:
            event = LoRaEvent(rxpk, NODE_REGISTRY)

            # ─ Deduplication
            if event.signature in SEEN:
                continue
            SEEN.append(event.signature)

            data = event.to_dict()
            logger.write_event(data)

            # ─ Print Decoded Event
            print("\n--- DECODED EVENT ---")
            for k, v in data.items():
                print(f"{k}: {v}")

            # ─ Dispatch Based on Target
            if event.target == "web_ingestor":
                print("[dispatcher] → Routed to: web_ingestor subsystem")
                handle_web_ingestor(data)
            elif event.target == "weather":
                print("[dispatcher] → Routed to: weather subsystem")
                handle_weather(data)
            elif event.target == "telemetry":
                print("[dispatcher] → Routed to: telemetry subsystem")
                handle_telemetry(data)
            else:
                print(f"[dispatcher] Unknown target: {event.target}")

        except Exception as e:
            print(f"[dispatcher] Failed to process rxpk: {e}")


# ─── Main Entry Point ──────────────────────────────────────────────
if __name__ == "__main__":
    listener = UDPListener(handle_push_data_callback=handle_push_data)
    listener.listen_loop()
