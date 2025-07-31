"""
birdnet_listener_watcher.py
----------------------------

This script runs as a background systemd service to monitor BirdNET-Pi's SQLite database
(birds.db) and automatically transmit the most recent detection over LoRa using a RAK RUI3 node.

Deployment:
- Registered as a systemd service under: birdnet_listener_watcher.service
- Automatically starts on boot and runs continuously in the background

Core Functions:
- Watches birds.db for changes using watchdog
- On new detection, extracts the most recent row
- Encodes detection info into a compact Avis payload (timestamp, taxonomy, confidence)
- Sends payload as binary hex via AT+SEND through UART using RUI3Driver

Technical Notes:
- Database path is hardcoded: /home/FLC/BirdNET-Pi/scripts/birds.db
- LoRa settings are fixed for outbound payloads
- Confidence is bucketed into 3-bit bins using internal static method
- UART port and Protocol encoding rely on local project modules

This script is stable and functional, but should be modularized in future versions
to separate database, protocol, and transmission logic.

To check service status:
  sudo systemctl status birdnet_listener_watcher.service

To manually run:
  python3 birdnet_listener_watcher.py
"""
#!/usr/bin/env python3
import time
import sqlite3
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from protocol import Protocol
from send_top_detection import RUI3Driver  # or import your helper function

DB_PATH = Path('/home/FLC/BirdNET-Pi/scripts/birds.db')

class DBChangeHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.last_rowid = None  # track what we've already sent

    def on_modified(self, event):
        if Path(event.src_path) != DB_PATH:
            return

        # give SQLite a moment to finish the write
        time.sleep(0.1)

        try:
            conn = sqlite3.connect(f'file:{DB_PATH}?mode=ro', uri=True, timeout=5)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            # pull the very latest row
            cur.execute('''
                SELECT rowid, Date, Time, Com_Name, Sci_Name, Confidence, File_Name
                  FROM detections
                 ORDER BY rowid DESC
                 LIMIT 1
            ''')
            row = cur.fetchone()
            conn.close()

            if not row:
                return

            # if it's the same rowid as last time, skip it
            if row['rowid'] == self.last_rowid:
                return
            self.last_rowid = row['rowid']

            # build a dict for convenience
            data = {
                'date': row['Date'],
                'time': row['Time'],
                'common_name': row['Com_Name'],
                'scientific_name': row['Sci_Name'],
                'confidence': row['Confidence'],
                'file_name': row['File_Name'],
            }
            print("New detection:", data)

            # — now encode & send over LoRa! —
            ts_str = f"{data['date']}T{data['time']}Z"
            ts = int(time.mktime(time.strptime(ts_str, "%Y-%m-%dT%H:%M:%SZ")))

            # confidence binning (reuse your watcher logic)
            raw_conf = float(data['confidence'])
            conf_bin = DBChangeHandler._get_conf_bin(raw_conf)

            # protocol encoding
            proto    = Protocol()
            tax_code = proto.encode_taxonomy(data['common_name'])
            payload  = proto.encode_avis_event(ts, tax_code, conf_bin)

            # send via AT+SEND
            driver = RUI3Driver()
            hex_payload = payload.hex().upper()
            at_cmd      = f"AT+SEND=1:{hex_payload}"
            print("→", at_cmd)
            resp = driver.send_cmd(at_cmd)
            print("Module replied:", resp)
            driver.close()

        except sqlite3.OperationalError as e:
            print(f"[WARN] DB locked or unavailable: {e}")

    @staticmethod
    def _get_conf_bin(raw: float):
        bins = [
            (0.00, 0.5001, 0),
            (0.5001, 0.6005, 1),
            (0.6006, 0.7004, 2),
            (0.7005, 0.8000, 3),
            (0.8001, 0.8005, 4),
            (0.8006, 0.9000, 5),
            (0.9001, 0.9005, 6),
            (0.9006, 1.0000, 7),
        ]
        for lo, hi, b in bins:
            if lo <= raw <= hi:
                return b
        raise ValueError(f"Invalid confidence {raw}")

def start_db_watcher():
    obs = Observer()
    obs.schedule(DBChangeHandler(), str(DB_PATH.parent), recursive=False)
    obs.start()
    print(f"Watching {DB_PATH} for changes…")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        obs.stop()
    obs.join()

if __name__ == '__main__':
    start_db_watcher()