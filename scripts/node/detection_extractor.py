"""
detection_extractor.py
----------------------

Queries BirdNET-Pi’s SQLite database and retrieves the latest detection
from the 'detections' table.

Returns:
    A dictionary with the latest row fields:
      - Date
      - Time
      - Com_Name
      - Sci_Name
      - Confidence
      - File_Name

Returns None if the DB is locked or no row is found.

Usage:
    from detection_extractor import get_latest_detection
    row = get_latest_detection()
"""

import sqlite3
import time
import os
from pathlib import Path

DB_PATH = Path("/home/node1/BirdNET-Pi/scripts/birds.db")

def get_latest_detection():
    time.sleep(0.5)  # Give SQLite time to flush after fs event

    for attempt in range(5):
        try:
            if not DB_PATH.exists():
                raise sqlite3.OperationalError("Database file not found.")

            if not os.access(DB_PATH, os.R_OK):
                raise sqlite3.OperationalError("Database file not readable.")

            conn = sqlite3.connect(DB_PATH, timeout=5)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            cur.execute('''
                SELECT Date, Time, Com_Name, Sci_Name, Confidence, File_Name
                  FROM detections
                 ORDER BY rowid DESC
                 LIMIT 1
            ''')
            row = cur.fetchone()
            conn.close()

            if not row:
                print("[DEBUG] [detection_extractor] No detections found.")
                return None

            return dict(row)

        except sqlite3.OperationalError as e:
            print(f"[WARN] [detection_extractor] Attempt {attempt + 1}: {e}")
            time.sleep(0.2)

    print("[ERROR] [detection_extractor] Failed to read detection after retries.")
    return None