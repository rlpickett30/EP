"""
protocol.py
------------

This module defines the Protocol class used to encode and decode compact Avis detection
events as 8-byte binary payloads for LoRa transmission.

Each Avis event includes:
  - event_type   (uint8): fixed value of 1 for bird detections
  - timestamp    (uint32): seconds since epoch (UTC)
  - taxonomy     (uint16): mapped BirdNET common name as integer code
  - confidence   (uint8): binned confidence value (0–7)

Core Features:
- Loads encoding structure from structure_protocol.json
- Dynamically loads any attached mapping files (e.g., taxonomy, confidence scale)
- Provides encode/decode methods for both taxonomy and event payloads
- Supports both forward and reverse lookup of taxonomy codes

Intended Usage:
- Construct compact binary packets to transmit over constrained networks (e.g., LoRa)
- Decode incoming payloads to reconstruct original detection data

Assumes:
- JSON maps are stored in the same directory and optionally brace-less
- structure_protocol.json defines the binary format and field mappings

This protocol module is essential to the Avis system and serves as the schema layer
between raw BirdNET detections and LoRa-compatible data packets.
"""

import json
import struct
from pathlib import Path

# Base directory for all protocol JSON maps
BASE_DIR = Path(__file__).resolve().parent

def _load_json(filename: str) -> dict:
    """
    Load a (possibly brace-less) JSON map from BASE_DIR.
    If the file content isn't wrapped in {} already, add them.
    """
    path = BASE_DIR / filename
    raw = path.read_text().strip()
    if not raw.startswith('{'):
        raw = '{' + raw + '}'
    return json.loads(raw)

class Protocol:
    """
    Protocol for Avis 8-byte detection events:
      - event_type (uint8)
      - timestamp  (uint32)
      - taxonomy   (uint16)
      - confidence (uint8)
    Maps for taxonomy and confidence are loaded automatically.
    """
    def __init__(self):
        # load the structure definition
        struct_def = _load_json('structure_protocol.json')['avis_event']
        self._format = struct_def['format']
        self._fields = struct_def['fields']

        # load any maps (e.g. taxonomy, confidence)
        self._maps = {}
        for field in self._fields:
            if 'map' in field:
                self._maps[field['name']] = _load_json(field['map'])

        # build reverse lookup for taxonomy
        self._tax_map = self._maps.get('taxonomy', {})
        self._rev_tax = {v: k for k, v in self._tax_map.items()}

    def encode_taxonomy(self, common_name: str) -> int:
        """
        Encode a common name into its taxonomy code.
        Returns 0 ('Unknown') if the name is not found.
        """
        return self._tax_map.get(common_name, 0)

    def decode_taxonomy(self, code: int) -> str:
        """
        Decode a taxonomy code back to its common name.
        Returns '<unknown {code}>' if the code is unrecognized.
        """
        return self._rev_tax.get(code, f'<unknown {code}>')

    def encode_avis_event(self, timestamp: int, tax_code: int, conf_bin: int) -> bytes:
        # pack event_type=1, timestamp, taxonomy, confidence
        return struct.pack(self._format, 1, timestamp, tax_code, conf_bin)

    def decode_avis_event(self, data: bytes):
        # unpack according to the same format; ignore extra fields if any
        unpacked = struct.unpack(self._format, data)
        _, ts, tax, conf = unpacked[:4]
        return ts, tax, conf