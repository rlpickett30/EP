"""
udp_listener.py
----------------

This script serves as the central LoRaWAN UDP packet listener for the EnviroPulse gateway.
It listens for incoming packets on port 1700 (UDP), decrypts any valid LoRaWAN uplinks,
decodes embedded Avis event payloads, and appends results to a rolling JSON log file.

Core Responsibilities:
- Bind to 0.0.0.0:1700 and listen for PUSH_DATA and PULL_DATA packets from LoRaWAN nodes
- Acknowledge valid packets with PUSH_ACK or PULL_ACK
- Parse, deduplicate, and decrypt FRMPayload using node-specific AppSKeys
- Decode Avis-format binary messages using Protocol
- Log the decoded content with timestamps and metadata to udp_listener_log.json

Additional Features:
- Loads node keys from node_registry.json for per-device decryption
- Deduplicates packets using a short-term memory (deque)
- Prints both raw and decoded event info to console for debugging
- Supports modular decoding of Avis messages using the project protocol

Limitations / To Refactor:
- This script is too large and would benefit from modular decomposition:
  - Separate packet parsing, logging, and decoding logic into their own modules
  - Introduce formal logging and error handling
  - Parameterize config paths and ports

Despite its size, this script is stable and performs all core gateway-side decoding
and logging functions for the system. It is suitable for production use in its
current form and should only be modified with care.

Run with:
  python udp_listener.py
"""

import socket
import struct
import json
import base64
import time
from datetime import datetime, timezone
from Crypto.Cipher import AES
from pathlib import Path
from collections import deque

from protocol import Protocol

# Globals
UDP_IP = "0.0.0.0"
UDP_PORT = 1700
LOG_PATH = Path("udp_listener_log.json")
seen_messages = deque(maxlen=100)


def lorawan_payload_decrypt(appskey_hex, devaddr_hex, fcnt, direction, payload_hex):
    appskey = bytes.fromhex(appskey_hex)
    devaddr = bytes.fromhex(devaddr_hex)[::-1]  # LSB
    fcnt_bytes = fcnt.to_bytes(4, 'little')
    payload = bytes.fromhex(payload_hex)

    block = b'\x01' + b'\x00'*4 + bytes([direction]) + devaddr + fcnt_bytes + b'\x00' + b'\x01'
    cipher = AES.new(appskey, AES.MODE_ECB)
    s_block = cipher.encrypt(block)
    return bytes(a ^ b for a, b in zip(payload, s_block))


def load_node_registry(path="node_registry.json"):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        print("Failed to load node registry:", e)
        return {}


def init_log():
    if not LOG_PATH.exists():
        with open(LOG_PATH, 'w') as f:
            json.dump([], f, indent=2)


def append_log(entry):
    try:
        with open(LOG_PATH, 'r+') as f:
            data = json.load(f)
            data.append(entry)
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()
    except Exception as e:
        print(f"[ERROR] Unable to write to log file: {e}")


def extract_json_segment(data):
    try:
        start = data.find(b'{')
        end = data.rfind(b'}')
        if start == -1 or end == -1 or end <= start:
            return None
        segment = data[start:end+1]
        return json.loads(segment.decode('utf-8', errors='ignore'))
    except Exception as e:
        print(f"[WARN] Failed to extract JSON segment: {e}")
        return None


def handle_push_data(data, addr, token, version, sock, node_registry):
    sock.sendto(struct.pack("!B2sB", version, token, 0x01), addr)
    print("Sent PUSH_ACK")

    payload = extract_json_segment(data)
    if not payload:
        print("[WARN] No valid JSON payload found in PUSH_DATA")
        return

    for rx in payload.get("rxpk", []):
        try:
            raw = base64.b64decode(rx.get("data", ""))
        except Exception:
            print("[WARN] Invalid base64 in rxpk data")
            continue

        mhdr = raw[0]
        devaddr = raw[1:5][::-1].hex().upper()
        fctrl = raw[5]
        fcnt = int.from_bytes(raw[6:8], "little")
        fport = raw[8]
        frm_hex = raw[9:-4].hex()
        mic = raw[-4:].hex()
        sig = f"{devaddr}-{fcnt}-{frm_hex}"

        if sig in seen_messages:
            continue
        seen_messages.append(sig)

        print(f"\n--- LoRaWAN Uplink Detected ---")
        print(f"DevAddr:    {devaddr}")
        print(f"FCnt:       {fcnt}")
        print(f"FPort:      {fport}")
        print(f"Encrypted FRMPayload (hex): {frm_hex}")
        print(f"MIC:        {mic}")

        appskey = node_registry.get(devaddr, {}).get("appskey")
        if not appskey:
            print(f"[WARN] No AppSKey for {devaddr}")
            continue

        decrypted = lorawan_payload_decrypt(appskey, devaddr, fcnt, 0, frm_hex)
        decrypted_hex = decrypted.hex().upper()
        print(f"Decrypted bytes:   {decrypted}")
        print(f"Decrypted hex:     {decrypted_hex}")

        entry = {
            "received_at": datetime.now(timezone.utc).isoformat(),
            "devaddr": devaddr,
            "fcnt": fcnt,
            "fport": fport,
            "encrypted_frm": frm_hex,
            "mic": mic,
            "decrypted_hex": decrypted_hex
        }

        try:
            proto = Protocol()
            decoded = proto.decode(decrypted)

            print("\n--- DECODED EVENT ---")
            for k, v in decoded.items():
                print(f" {k}: {v}")

            if "timestamp" in decoded:
                decoded["event_timestamp"] = datetime.utcfromtimestamp(decoded["timestamp"]).isoformat() + 'Z'

            entry.update(decoded)

        except Exception as e:
            print(f"[WARN] Failed to decode payload: {e}")
            entry["decode_error"] = str(e)

        append_log(entry)


def handle_pull_data(data, addr, token, version, sock):
    sock.sendto(struct.pack("!B2sB", version, token, 0x04), addr)
    print("Sent PULL_ACK")


def main():
    init_log()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"Listening on UDP port {UDP_PORT}…")

    node_registry = load_node_registry()

    while True:
        data, addr = sock.recvfrom(4096)
        if len(data) < 4:
            continue
        version = data[0]
        token = data[1:3]
        pkt = data[3]

        if pkt == 0x00:
            handle_push_data(data, addr, token, version, sock, node_registry)
        elif pkt == 0x02:
            handle_pull_data(data, addr, token, version, sock)


if __name__ == "__main__":
    main()
