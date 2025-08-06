"""

db_watcher.py
-------------

Monitors BirdNET-Pi’s SQLite database (birds.db) using watchdog and triggers a callback
whenever the detections table is updated with a new row.

This module is intended to be used by dispatcher.py as part of the EnviroPulse event loop.

Behavior:
- Watches birds.db for changes on disk
- On modification, queries the most recent rowid
- Ignores duplicate rowids to prevent reprocessing the same detection
- Delays briefly to allow SQLite to finish writing before querying
- Executes a user-provided callback function when a new row appears

Notes:
- Database path is hardcoded to: /home/FLC/BirdNET-Pi/scripts/birds.db
- Uses watchdog for efficient event monitoring
- This module does not return the full detection; just signals a new entry
- Detection parsing is handled by detection_extractor.py

To use:
    from db_watcher import start_db_watch

    def on_new_detection():
        print("Detected new row!")

    observer = start_db_watch(on_new_detection)
"""

import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

DB_PATH = Path('/home/node1/BirdNET-Pi/scripts/birds.db')

class DBChangeHandler(FileSystemEventHandler):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.last_rowid = None

    def on_modified(self, event):
        if Path(event.src_path) != DB_PATH:
            return

        time.sleep(0.1)  # let SQLite finish writing

        try:
            import sqlite3
            conn = sqlite3.connect(f'file:{DB_PATH}?mode=ro', uri=True, timeout=5)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            cur.execute('''
                SELECT rowid FROM detections
                 ORDER BY rowid DESC
                 LIMIT 1
            ''')
            row = cur.fetchone()
            conn.close()

            if not row:
                return

            # skip duplicates
            if row['rowid'] == self.last_rowid:
                return
            self.last_rowid = row['rowid']

            # trigger user-defined callback
            self.callback()

        except sqlite3.OperationalError as e:
            print(f"[WARN] DB locked or unavailable: {e}")

def start_db_watch(callback):
    observer = Observer()
    handler = DBChangeHandler(callback)
    observer.schedule(handler, str(DB_PATH.parent), recursive=False)
    observer.start()
    print(f"Watching {DB_PATH} for changes...")
    return observer  # caller should `.stop()` and `.join()` on shutdown