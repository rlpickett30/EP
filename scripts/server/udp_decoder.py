"""
udp_decoder.py
--------------

Defines LoRaEvent, a class that represents a decoded LoRaWAN event.

Responsibilities:
- Parse base64 rxpk from Semtech UDP JSON
- Extract and decrypt LoRaWAN fields using AppSKey
- Decode binary payload using Protocol maps
- Normalize into a dict for routing and logging

Limitations:
- Uplink-only (ABP)
- MIC field is parsed but not validated
- Target is hardcoded as "web_ingestor" for now

Usage:
    event = LoRaEvent(rxpk, node_registry)
    print(event.target)
    print(event.to_dict())
"""

import base64
from datetime import datetime, timezone
from lorawan_decryptor import decrypt_frmpayload
from protocol import Protocol


class LoRaEvent:
    def __init__(self, rxpk: dict, node_registry: dict):
        # ─── Decode Semtech UDP format ─────────────────────────────
        self.raw = base64.b64decode(rxpk.get("data", ""))
        self.devaddr = self.raw[1:5][::-1].hex().upper()
        self.fcnt = int.from_bytes(self.raw[6:8], "little")
        self.fport = self.raw[8]
        self.frm_payload_hex = self.raw[9:-4].hex()
        self.mic = self.raw[-4:].hex()
        self.signature = f"{self.devaddr}-{self.fcnt}-{self.frm_payload_hex}"

        # ─── Lookup AppSKey and decrypt payload ────────────────────
        self.appskey = node_registry.get(self.devaddr, {}).get("appskey")
        if not self.appskey:
            raise KeyError(f"No AppSKey found for DevAddr {self.devaddr}")

        self.decrypted = decrypt_frmpayload(
            self.appskey,
            self.devaddr,
            self.fcnt,
            0,  # direction: 0 = uplink
            self.frm_payload_hex
        )
        self.decrypted_hex = self.decrypted.hex().upper()

        # ─── Decode binary payload using Protocol maps ─────────────
        proto = Protocol()
        self.decoded = proto.decode(self.decrypted)

        # ─── Timestamp (optional, from payload) ────────────────────
        if "timestamp" in self.decoded:
            self.decoded["event_timestamp"] = datetime.utcfromtimestamp(
                self.decoded["timestamp"]
            ).isoformat() + "Z"

        # ─── Explicit routing target override ──────────────────────
        self.target = "web_ingestor"
        self.decoded["target"] = self.target

    def to_dict(self):
        return {
            "received_at": datetime.now(timezone.utc).isoformat(),
            "devaddr": self.devaddr,
            "fcnt": self.fcnt,
            "fport": self.fport,
            "encrypted_frm": self.frm_payload_hex,
            "mic": self.mic,
            "decrypted_hex": self.decrypted_hex,
            "raw_signature": self.signature,
            **self.decoded
        }
