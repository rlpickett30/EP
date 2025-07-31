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
from pathlib import Path

DB_PATH = Path("/home/FLC/BirdNET-Pi/scripts/birds.db")

def get_latest_detection():
    try:
        conn = sqlite3.connect(f'file:{DB_PATH}?mode=ro', uri=True, timeout=5)
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
            return None

        return dict(row)

    except sqlite3.OperationalError as e:
        print(f"[WARN] DB unavailable or locked: {e}")
        return None
