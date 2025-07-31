"""
udp_logger.py
-------------

Handles structured daily logging for EnviroPulse server events.

Responsibilities:
- Create EP/logs/ directory if it doesn't exist
- Rotate logs daily using MM_DD_YYYY.json filename format
- Append decoded event dictionaries to the current day's log
- Ensure valid JSON structure (read-modify-write with truncate)

Directory structure:
  EP/logs/07_31_2025.json      ← Daily log for July 31, 2025
  EP/logs/08_01_2025.json      ← Daily log for August 1, 2025

Usage:
    from udp_logger import Logger
    logger = Logger(base_dir="EP/logs")
    logger.write_event(event_dict)
"""

import json
from pathlib import Path
from datetime import datetime


class Logger:
    def __init__(self, base_dir="EP/logs"):
        self.log_dir = Path(base_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def _get_today_path(self):
        now = datetime.utcnow()
        filename = now.strftime("%m_%d_%Y.json")
        return self.log_dir / filename

    def write_event(self, event: dict):
        path = self._get_today_path()
        try:
            if not path.exists():
                with open(path, "w") as f:
                    json.dump([event], f, indent=2)
            else:
                with open(path, "r+") as f:
                    data = json.load(f)
                    data.append(event)
                    f.seek(0)
                    json.dump(data, f, indent=2)
                    f.truncate()
        except Exception as e:
            print(f"[udp_logger] Failed to write event: {e}")
