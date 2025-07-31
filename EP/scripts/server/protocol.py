"""
protocol.py
-----------

Handles binary encoding and decoding of EnviroPulse events using
structure_protocol.json, event_type_map.json, and taxonomy_map.json.

Guarantees crash-proof operation:
- Invalid events will raise informative errors or return fallback
- Unknown taxonomy or type values are replaced with "Unknown"/0
"""

import struct
import json
from pathlib import Path


class Protocol:
    def __init__(self):
        base = Path(__file__).resolve().parent  # <— SAFELY resolves absolute path
        self._structure = self._load_json(base / "structure_protocol.json")
        self._event_map = self._load_json(base / "event_type_map.json")
        self._taxonomy_map = self._load_json(base / "taxonomy_map.json")
        self._confidence_map = self._load_json(base / "confidence_scale_map.json")

        self._reverse_event_map = {v: k for k, v in self._event_map.items()}
        self._reverse_taxonomy_map = {v: k for k, v in self._taxonomy_map.items()}
        self._reverse_confidence_map = {v: k for k, v in self._confidence_map.items()}

    def _load_json(self, path: Path) -> dict:
        try:
            raw = path.read_text().strip()
            return json.loads(raw if raw.startswith("{") else "{" + raw + "}")
        except Exception as e:
            print(f"[ERROR] Failed to load {path.name}: {e}")
            return {}

    def encode(self, event: dict) -> bytes:
        try:
            event_type_str = event.get("event_type", "Unknown")
            struct_def = self._structure.get(event_type_str)
            if not struct_def:
                raise ValueError(f"Unknown or unsupported event_type: '{event_type_str}'")

            fmt = struct_def["format"]
            fields = struct_def["fields"]

            values = []
            for field in fields:
                name = field["name"]
                if name == "event_type":
                    values.append(self._event_map.get(event_type_str, 0))
                elif "map" in field and name == "taxonomy":
                    values.append(self._taxonomy_map.get(event.get("common_name", "Unknown"), 0))
                elif "map" in field and name == "confidence":
                    values.append(self._confidence_map.get(event.get("confidence_label", "Unknown"), 0))
                else:
                    if name not in event:
                        raise KeyError(f"Missing field '{name}' in event")
                    values.append(event[name])

            return struct.pack(fmt, *values)

        except Exception as e:
            print(f"[ERROR] Failed to encode event: {e}")
            return b''

    def decode(self, data: bytes) -> dict:
        if len(data) < 1:
            print("[ERROR] Cannot decode empty payload.")
            return {"event_type": "decode_error", "raw": data.hex()}

        try:
            event_type_id = data[0]
            event_type_str = self._reverse_event_map.get(event_type_id, "Unknown")
            struct_def = self._structure.get(event_type_str)
            if not struct_def:
                raise ValueError(f"Unknown event_type ID: {event_type_id}")

            fmt = struct_def["format"]
            expected_len = struct.calcsize(fmt)
            if len(data) != expected_len:
                raise ValueError(f"Incorrect payload length for {event_type_str}: expected {expected_len}, got {len(data)}")

            fields = struct_def["fields"]
            unpacked = struct.unpack(fmt, data)
            event = {"event_type": event_type_str}

            for i, field in enumerate(fields):
                name = field["name"]
                if name == "event_type":
                    continue
                elif "map" in field and name == "taxonomy":
                    event["common_name"] = self._reverse_taxonomy_map.get(unpacked[i], "Unknown")
                elif "map" in field and name == "confidence":
                    event["confidence_label"] = self._reverse_confidence_map.get(unpacked[i], "Unknown")
                else:
                    event[name] = unpacked[i]

            return event

        except Exception as e:
            print(f"[ERROR] Failed to decode payload: {e}")
            return {
                "event_type": "decode_error",
                "raw": data.hex(),
                "error": str(e)
            }
